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

    # [재훈] 2026-02-26
    # 컬럼 추가
        # extraction_time_seconds=extraction_time_seconds,
        # summary_time_seconds=summary_time_seconds,
        # file_size_bytes=file_size_bytes,
        # total_pages=total_pages,
        # successful_pages=successful_pages,
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

# [재훈] 2026-02-26
# 추가: UI용 DB 문서 목록 조회 API (기존 로직 수정 없이 추가)
@router.get("/documents")
def list_all_documents(db: Session = Depends(get_db)):
    docs = db.query(PdfDocument).order_by(PdfDocument.id.asc()).all()
    
    return [
        {
            "id": doc.id,
            "filename": doc.filename,
            "summary": (doc.summary or "(요약 없음)")[:80] + "..." if doc.summary else "(요약 없음)",
            "model_used": doc.model_used or "-",
            "char_count": f"{doc.char_count:,}" if doc.char_count else "-",
            "created_at": doc.created_at.strftime("%Y-%m-%d %H:%M") if doc.created_at else "-",
          
            # [재훈] 2026-02-26 
            # 컬럼 추가 
            "extraction_time": f"{doc.extraction_time_seconds:.2f}초" if doc.extraction_time_seconds is not None else "-",
            "summary_time": f"{doc.summary_time_seconds:.2f}초" if doc.summary_time_seconds is not None else "-",
            "file_size_mb": f"{doc.file_size_bytes / (1024 * 1024):.1f} MB" if doc.file_size_bytes is not None else "-",
            "pages": f"{doc.successful_pages or 0}/{doc.total_pages or '?'}"
                     if doc.total_pages is not None else "-",
            "translation_time": f"{doc.translation_time_seconds:.2f}초" if doc.translation_time_seconds is not None else "-",
            "translation_model": doc.translation_model or "-",
            "original_translation_preview": (doc.original_translation or "")[:80] + "..." if doc.original_translation else "-",
            "summary_translation_preview": (doc.summary_translation or "")[:80] + "..." if doc.summary_translation else "-",
            "status": "완료" if doc.successful_pages == doc.total_pages and doc.total_pages else "부분" if doc.successful_pages else "-"
        }
        for doc in docs
    ]

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