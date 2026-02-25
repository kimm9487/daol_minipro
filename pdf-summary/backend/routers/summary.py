from fastapi import APIRouter, UploadFile, File, Form, Depends
from fastapi.responses import Response
from sqlalchemy.orm import Session
from urllib.parse import quote
from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text, get_available_models
from database import get_db, PdfDocument
import datetime

router = APIRouter()


@router.post("/summarize")
async def summarize_pdf(
    file: UploadFile = File(...),
    model: str = Form(default="gemma3:latest"),
    db: Session = Depends(get_db),          # ← DB 세션 추가
):
    # 1. PDF 텍스트 추출
    extracted_text = await extract_text_from_pdf(file)

    # 2. AI 요약
    summary = await summarize_text(extracted_text, model=model)

    # 3. DB 저장  ← 이 부분이 핵심!
    doc = PdfDocument(
        filename=file.filename,
        extracted_text=extracted_text,
        summary=summary,
        model_used=model,
        char_count=len(extracted_text),
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)

    return {
        "id": doc.id,
        "filename": file.filename,
        "original_length": len(extracted_text),
        "extracted_text": extracted_text,
        "summary": summary,
        "model_used": model,
        "created_at": datetime.datetime.now().isoformat(),
    }


@router.get("/models")
async def list_models():
    models = await get_available_models()
    return {"models": models}


@router.post("/download")
async def download_summary(summary: str = Form(...), filename: str = Form(default="summary")):
    content = summary.encode("utf-8")
    safe_filename = filename.replace(".pdf", "") + "_요약.txt"

    return Response(
        content=content,
        media_type="text/plain; charset=utf-8",
        headers={
            "Content-Disposition": f"attachment; filename*=UTF-8''{quote(safe_filename)}"
        },
    )