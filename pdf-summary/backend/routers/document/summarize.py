from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Request
from sqlalchemy.orm import Session
import json
import time
import datetime

from services.pdf_service import extract_text_from_pdf
from services.ai_service import summarize_text, categorize_document
from database import get_db, PdfDocument, can_user_access_document, log_admin_activity

summarize_router = APIRouter(tags=["Summarization & Extraction"])


# Helper function to create a document entry before summarization
async def _build_extraction_document(
    request: Request,
    file: UploadFile,
    user_id: int,
    ocr_model: str,
    is_important: bool,
    password: str,
    is_public: bool,
    db: Session,
):
    extraction_result = await extract_text_from_pdf(file, ocr_model=ocr_model)
    extracted_text = extraction_result["text"]
    extraction_time = extraction_result["processing_time"]

    await file.seek(0)
    file_size = len(await file.read())
    await file.seek(0)

    stored_password = None
    if is_important:
        if not password or len(password) != 4 or not password.isdigit():
            raise HTTPException(
                status_code=400,
                detail="중요문서는 4자리 숫자 비밀번호가 필요합니다."
            )
        stored_password = password
    else:
        stored_password = None

    doc = PdfDocument(
        user_id=user_id,
        filename=file.filename,
        extracted_text=extracted_text,
        summary=None,
        ocr_model=extraction_result.get("ocr_model"),
        model_used=None,
        char_count=len(extracted_text),
        file_size_bytes=file_size,
        total_pages=extraction_result["total_pages"],
        successful_pages=extraction_result["successful_pages"],
        extraction_time_seconds=round(extraction_time, 3),
        summary_time_seconds=None,
        is_important=is_important,
        password=stored_password,
        is_public=is_public,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    
    try:
        category_start = time.time()
        category = await categorize_document(title=file.filename)
        category_time = time.time() - category_start
        
        doc.category = category
        db.commit()
        print(f"✅ 문서 카테고리 분류 완료: {category} ({category_time:.2f}초)")
    except Exception as e:
        print(f"⚠️ 카테고리 분류 실패: {str(e)}")
        doc.category = "기타"
        db.commit()
    
    log_admin_activity(
        db=db,
        admin_user_id=user_id,
        action="DOCUMENT_UPLOADED",
        target_type="DOCUMENT",
        target_id=doc.id,
        details=json.dumps({
            "filename": file.filename,
            "file_size_bytes": file_size,
            "ocr_model": extraction_result["ocr_model"],
            "category": doc.category,
            "is_important": is_important,
            "is_public": is_public
        }),
        ip_address=request.client.host
    )

    return {
        "id": doc.id,
        "filename": file.filename,
        "original_length": len(extracted_text),
        "extracted_text": extracted_text,
        "summary": None,
        "model_used": None,
        "ocr_model": extraction_result["ocr_model"],
        "category": doc.category,
        "created_at": datetime.datetime.now().isoformat(),
        "is_important": doc.is_important,
        "password": doc.password,
        "is_public": doc.is_public,
        "timing": {
            "extraction_time": f"{extraction_time:.2f}초",
            "summary_time": None,
            "total_time": f"{extraction_time:.2f}초"
        },
        "extraction_info": {
            "total_pages": extraction_result["total_pages"],
            "successful_pages": extraction_result["successful_pages"],
            "char_count": extraction_result["char_count"],
            "file_size_mb": f"{file_size / (1024*1024):.2f}MB"
        }
    }


@summarize_router.post("/extract")
async def extract_pdf(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Form(...),
    ocr_model: str = Form(default="pypdf2"),
    is_important: bool = Form(default=False),
    password: str = Form(default=None),
    is_public: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    """(Step 1) Extracts text from a PDF file and creates a document record."""
    return await _build_extraction_document(
        request=request,
        file=file,
        user_id=user_id,
        ocr_model=ocr_model,
        is_important=is_important,
        password=password,
        is_public=is_public,
        db=db,
    )


@summarize_router.post("/summarize-document")
async def summarize_extracted_document(
    request: Request,
    document_id: int = Form(...),
    user_id: int = Form(...),
    model: str = Form(default="gemma3:latest"),
    db: Session = Depends(get_db),
):
    """(Step 2) Summarizes the extracted text of an existing document."""
    if not can_user_access_document(db, user_id, document_id):
        raise HTTPException(status_code=403, detail="이 문서에 접근할 권한이 없습니다.")

    doc = db.query(PdfDocument).filter(PdfDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
    if not doc.extracted_text:
        raise HTTPException(status_code=400, detail="먼저 텍스트를 추출해주세요.")

    summary_start = time.time()
    summary = await summarize_text(doc.extracted_text, model=model)
    summary_time = time.time() - summary_start

    doc.summary = summary
    doc.model_used = model
    doc.summary_time_seconds = round(summary_time, 3)
    doc.updated_at = datetime.datetime.now()
    db.commit()
    db.refresh(doc)

    log_admin_activity(
        db=db,
        admin_user_id=user_id,
        action="DOCUMENT_SUMMARIZED",
        target_type="DOCUMENT",
        target_id=doc.id,
        details=json.dumps({
            "filename": doc.filename,
            "llm_model": model,
            "summary_length": len(summary),
        }),
        ip_address=request.client.host,
    )

    return {
        "id": doc.id,
        "document_id": doc.id,
        "filename": doc.filename,
        "extracted_text": doc.extracted_text,
        "summary": doc.summary,
        "ocr_model": doc.ocr_model,
        "model_used": doc.model_used,
        "summary_time": f"{summary_time:.2f}초",
        "created_at": doc.created_at.isoformat() if doc.created_at else None,
        "updated_at": doc.updated_at.isoformat() if doc.updated_at else None,
    }


@summarize_router.post("/summarize")
async def summarize_pdf_legacy(
    request: Request,
    file: UploadFile = File(...),
    user_id: int = Form(...),
    model: str = Form(default="gemma3:latest"),
    ocr_model: str = Form(default="pypdf2"),
    is_important: bool = Form(default=False),
    password: str = Form(default=None),
    is_public: bool = Form(default=True),
    db: Session = Depends(get_db),
):
    """(Legacy) Extracts and summarizes a PDF in a single call."""
    extracted = await _build_extraction_document(
        request=request,
        file=file,
        user_id=user_id,
        ocr_model=ocr_model,
        is_important=is_important,
        password=password,
        is_public=is_public,
        db=db,
    )

    summarize_result = await summarize_extracted_document(
        request=request,
        document_id=extracted["id"],
        user_id=user_id,
        model=model,
        db=db,
    )
    extracted["summary"] = summarize_result["summary"]
    extracted["model_used"] = summarize_result["model_used"]
    extracted["timing"]["summary_time"] = summarize_result["summary_time"]
    return extracted
