from fastapi import APIRouter, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from sqlalchemy import text
import datetime

from database import get_db, PdfDocument, User

system_router = APIRouter(tags=["Admin-System"])

@system_router.get("/database-status")
async def get_database_status(db: Session = Depends(get_db)):
    """
    Retrieves database status and statistical information.
    """
    try:
        version_result = db.execute(text("SELECT VERSION()"))
        db_version = version_result.fetchone()[0]
       
        tables_result = db.execute(text("SHOW TABLES"))
        tables = [row[0] for row in tables_result.fetchall()]
       
        table_structure = None
        if 'pdf_documents' in tables:
            structure_result = db.execute(text("DESCRIBE pdf_documents"))
            table_structure = [
                {
                    "field": row[0],
                    "type": row[1],
                    "null": row[2],
                    "key": row[3],
                    "default": row[4],
                    "extra": row[5]
                }
                for row in structure_result.fetchall()
            ]
       
        data_stats = {}
        if 'pdf_documents' in tables:
            total_docs = db.query(PdfDocument).count()
            original_translated = db.query(PdfDocument).filter(PdfDocument.original_translation.isnot(None)).count()
            summary_translated = db.query(PdfDocument).filter(PdfDocument.summary_translation.isnot(None)).count()
            recent_docs = db.query(PdfDocument).order_by(PdfDocument.created_at.desc()).limit(5).all()
            avg_extraction_time = db.execute(text("SELECT AVG(extraction_time_seconds) FROM pdf_documents WHERE extraction_time_seconds IS NOT NULL")).scalar()
            avg_summary_time = db.execute(text("SELECT AVG(summary_time_seconds) FROM pdf_documents WHERE summary_time_seconds IS NOT NULL")).scalar()
            avg_translation_time = db.execute(text("SELECT AVG(translation_time_seconds) FROM pdf_documents WHERE translation_time_seconds IS NOT NULL")).scalar()
           
            data_stats = {
                "total_documents": total_docs,
                "original_translated": original_translated,
                "summary_translated": summary_translated,
                "translation_rate": f"{(original_translated/total_docs*100):.1f}%" if total_docs > 0 else "0%",
                "recent_documents": [
                    {
                        "id": doc.id,
                        "filename": doc.filename,
                        "created_at": doc.created_at.isoformat() if doc.created_at else None,
                        "has_original_translation": bool(doc.original_translation),
                        "has_summary_translation": bool(doc.summary_translation),
                        "char_count": doc.char_count,
                        "total_pages": doc.total_pages,
                        "file_size_mb": f"{doc.file_size_bytes / (1024*1024):.2f}" if doc.file_size_bytes else None
                    }
                    for doc in recent_docs
                ],
                "average_processing_times": {
                    "extraction_seconds": float(avg_extraction_time) if avg_extraction_time else None,
                    "summary_seconds": float(avg_summary_time) if avg_summary_time else None,
                    "translation_seconds": float(avg_translation_time) if avg_translation_time else None
                }
            }
       
        return {
            "database_connection": "✅ 연결 성공",
            "database_version": db_version,
            "tables": tables,
            "pdf_documents_table_exists": 'pdf_documents' in tables,
            "table_structure": table_structure,
            "data_statistics": data_stats,
            "timestamp": datetime.datetime.now().isoformat()
        }
       
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error": "데이터베이스 상태 확인 실패",
                "message": str(e)
            }
        )

@system_router.post("/current-username")
async def get_current_username(
    user_id: str = Form(..., description="localStorage에 저장된 userName (full_name 또는 username)"),
    db: Session = Depends(get_db),
):
    """
    (Workaround) Returns the actual username for a given full_name to prevent auth errors on the frontend.
    """
    user = db.query(User).filter(User.username == user_id).first()
    if user:
        return {"username": user.username}

    user = db.query(User).filter(User.full_name == user_id).first()
    if user:
        return {"username": user.username}

    raise HTTPException(
        status_code=404,
        detail="사용자를 찾을 수 없습니다."
    )

