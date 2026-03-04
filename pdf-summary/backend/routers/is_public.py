from fastapi import APIRouter, UploadFile, File, Form, Depends, HTTPException, Body, Query  
from fastapi.responses import Response
from sqlalchemy.orm import Session, joinedload 
from sqlalchemy import text
from database import get_db, PdfDocument, can_user_access_document
router = APIRouter()

# ────────────────────────────────────────────────────────────────
# [오상진] 2026-03-03 추가: 마이페이지 문서 공개/비공개 상태 업데이트 엔드포인트
# ────────────────────────────────────────────────────────────────

@router.patch("/document/{document_id}/public")
async def toggle_document_public(
    document_id: int,
    user_id: int = Body(...),
    is_public: bool = Body(...),
    password: str = Body(None),  # [추가] 비밀번호를 선택적으로 받음
    db: Session = Depends(get_db),
):
    """
    문서의 공개/비공개 상태를 업데이트합니다. 
    비공개로 전환 시 비밀번호를 함께 설정할 수 있습니다.
    """
    # 1. 사용자 권한 확인
    if not can_user_access_document(db, user_id, document_id):
        raise HTTPException(status_code=403, detail="이 문서에 접근할 권한이 없습니다.")
   
    doc = db.query(PdfDocument).filter(PdfDocument.id == document_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="문서를 찾을 수 없습니다.")
   
    # 2. 비공개(is_public=False)로 전환 시 로직 처리
    if not is_public:
        # 비공개로 바꿀 때 비밀번호가 전달되었다면 유효성 검사 후 저장
        if password:
            if len(password) != 4 or not password.isdigit():
                raise HTTPException(status_code=400, detail="비밀번호는 숫자 4자리여야 합니다.")
            doc.password = password
            doc.is_important = True # 비밀번호가 있으면 중요 문서로 간주 (기존 로직 유지 시)
    else:
        # 공개로 전환 시 필요하다면 비밀번호를 초기화하거나 유지 (정책에 따라 결정)
        # doc.password = None 
        pass

    # 3. 공개 상태 업데이트
    doc.is_public = is_public
    db.commit()
    db.refresh(doc)
   
    return {
        "id": doc.id,
        "filename": doc.filename,
        "is_public": doc.is_public,
        "has_password": bool(doc.password),
        "message": f"문서가 {'공개' if is_public else '비공개'} 상태로 변경되었습니다."
    }

