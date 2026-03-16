import json
import datetime
from fastapi import APIRouter, Form, Query, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from sqlalchemy import desc
from database import get_db, User, UserSession, log_admin_activity

sessions_router = APIRouter(tags=["Session Management"])


# ────────────────────────────────────────────────────────────────
# 세션 관리 엔드포인트
# ────────────────────────────────────────────────────────────────

@sessions_router.get("/sessions/validate")
def validate_session(
    user_id: int = Query(...),
    session_token: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    현재 세션이 유효한지 검증 (강제 로그아웃 감지)
    """
    # 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return {"is_valid": False, "reason": "사용자를 찾을 수 없습니다."}
    
    # 세션 확인
    session = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.session_token == session_token
    ).first()
    
    if not session:
        return {"is_valid": False, "reason": "세션을 찾을 수 없습니다."}
    
    if not session.is_active:
        return {"is_valid": False, "reason": "강제 로그아웃"}
    
    # 만료 확인
    if session.expires_at and datetime.datetime.utcnow() > session.expires_at:
        return {"is_valid": False, "reason": "세션 만료"}
    
    return {"is_valid": True, "reason": "유효한 세션"}


@sessions_router.get("/sessions/current")
def get_current_sessions(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    현재 사용자의 활성 세션 목록 조회
    """
    # 사용자 확인
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 활성 세션 조회
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id,
        UserSession.is_active == True
    ).order_by(desc(UserSession.created_at)).all()
    
    return {
        "username": user.username,
        "sessions": [
            {
                "id": session.id,
                "session_token": session.session_token[:20] + "..." if session.session_token else "",  # 토큰 마스킹
                "created_at": session.created_at.isoformat() if session.created_at else None,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent[:50] if session.user_agent else "Unknown",  # 첫 50자만
                "is_active": session.is_active
            }
            for session in sessions
        ],
        "total": len(sessions)
    }


@sessions_router.delete("/sessions/{session_id}")
def logout_session(
    session_id: int,
    request: Request,
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    특정 세션 강제 로그아웃 (사용자 본인 또는 관리자만 가능)
    """
    # 세션 확인
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 권한 확인 (세션 소유자 또는 관리자)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    
    if session.user_id != user_id and user.role != 'admin':
        raise HTTPException(status_code=403, detail="다른 사용자의 세션을 종료할 권한이 없습니다.")
    
    # 세션 비활성화
    session.is_active = False
    db.commit()
    
    # 로그 기록
    log_admin_activity(
        db=db,
        admin_user_id=user_id,
        action="SESSION_TERMINATED",
        target_type="SESSION",
        target_id=session.id,
        details=json.dumps({
            "terminated_user_id": session.user_id,
            "terminated_by_admin": user.role == 'admin',
            "ip_address": session.ip_address
        }),
        ip_address=request.client.host
    )
    
    return {"message": "세션이 종료되었습니다.", "session_id": session_id}


@sessions_router.post("/logout")
def logout(
    request: Request,
    user_id: int = Form(...),
    session_token: str = Form(None),
    db: Session = Depends(get_db)
):
    """
    사용자 로그아웃 (현재 세션 종료)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="사용자를 찾을 수 없습니다.")
    
    # 세션 토큰이 있으면 해당 세션만 종료, 없으면 모든 활성 세션 종료
    if session_token:
        session = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.session_token == session_token
        ).first()
        if session:
            session.is_active = False
            db.commit()
    else:
        # 모든 활성 세션 종료
        sessions = db.query(UserSession).filter(
            UserSession.user_id == user_id,
            UserSession.is_active == True
        ).all()
        for session in sessions:
            session.is_active = False
        db.commit()
    
    # 로그 기록
    log_admin_activity(
        db=db,
        admin_user_id=user_id,
        action="USER_LOGOUT",
        target_type="USER",
        target_id=user_id,
        details=json.dumps({"username": user.username}),
        ip_address=request.client.host
    )
    
    return {"message": "로그아웃되었습니다."}


@sessions_router.get("/login-history")
def get_login_history(
    user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    사용자의 로그인 이력 조회 (최근 50개)
    """
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다.")
    
    # 로그인 이력 조회 (모든 세션, 비활성 포함)
    sessions = db.query(UserSession).filter(
        UserSession.user_id == user_id
    ).order_by(desc(UserSession.created_at)).limit(50).all()
    
    return {
        "username": user.username,
        "login_history": [
            {
                "session_id": session.id,
                "login_time": session.created_at.isoformat() if session.created_at else None,
                "expires_at": session.expires_at.isoformat() if session.expires_at else None,
                "ip_address": session.ip_address,
                "device": session.user_agent[:80] if session.user_agent else "Unknown",
                "is_active": session.is_active,
                "status": "활성" if session.is_active else "종료"
            }
            for session in sessions
        ],
        "total": len(sessions)
    }


@sessions_router.get("/admin/sessions")
def get_all_sessions(
    admin_user_id: int = Query(...),
    page: int = Query(1),
    limit: int = Query(100),
    db: Session = Depends(get_db)
):
    """
    관리자 전용: 모든 사용자의 세션 목록 조회
    """
    # 관리자 확인
    admin = db.query(User).filter(User.id == admin_user_id, User.role == 'admin').first()
    if not admin:
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")
    
    # 페이지네이션
    offset = (page - 1) * limit
    
    # 모든 활성 세션 조회
    sessions = db.query(UserSession).filter(
        UserSession.is_active == True
    ).order_by(desc(UserSession.created_at)).offset(offset).limit(limit).all()
    
    total = db.query(UserSession).filter(UserSession.is_active == True).count()
    
    session_list = []
    for session in sessions:
        user = db.query(User).filter(User.id == session.user_id).first()
        session_list.append({
            "session_id": session.id,
            "username": user.username if user else "미상",
            "user_id": session.user_id,
            "login_time": session.created_at.isoformat() if session.created_at else None,
            "ip_address": session.ip_address,
            "device": session.user_agent[:50] if session.user_agent else "Unknown",
            "expires_at": session.expires_at.isoformat() if session.expires_at else None
        })
    
    return {
        "sessions": session_list,
        "pagination": {
            "page": page,
            "limit": limit,
            "total": total,
            "total_pages": (total + limit - 1) // limit
        }
    }


@sessions_router.delete("/admin/sessions/{session_id}")
def admin_force_logout(
    session_id: int,
    request: Request,
    admin_user_id: int = Query(...),
    db: Session = Depends(get_db)
):
    """
    관리자 전용: 임의의 세션 강제 로그아웃
    """
    # 관리자 확인
    admin = db.query(User).filter(User.id == admin_user_id, User.role == 'admin').first()
    if not admin:
        raise HTTPException(status_code=403, detail="관리자만 접근 가능합니다.")
    
    # 세션 확인
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="세션을 찾을 수 없습니다.")
    
    # 자신의 세션은 강제 로그아웃할 수 없음
    if session.user_id == admin_user_id:
        raise HTTPException(status_code=403, detail="본인의 세션은 강제 로그아웃할 수 없습니다.")
    
    # 세션 비활성화
    session_user_id = session.user_id
    session.is_active = False
    db.commit()
    
    # 관리 로그 기록
    log_admin_activity(
        db=db,
        admin_user_id=admin_user_id,
        action="SESSION_TERMINATED_BY_ADMIN",
        target_type="SESSION",
        target_id=session_id,
        details=json.dumps({
            "terminated_user_id": session_user_id,
            "ip_address": session.ip_address,
            "admin_username": admin.username
        }),
        ip_address=request.client.host
    )
    
    return {"message": "세션이 강제 종료되었습니다.", "session_id": session_id}
