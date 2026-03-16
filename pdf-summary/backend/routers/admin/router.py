from fastapi import APIRouter
from .users import users_router
from .documents import documents_router
from .system import system_router

# 메인 admin 라우터를 생성하고, prefix와 tags를 설정합니다.
router = APIRouter(prefix="/api/admin", tags=["Admin"])

# 분리된 users와 documents 라우터를 메인 라우터에 포함시킵니다.
router.include_router(users_router)
router.include_router(documents_router)
router.include_router(system_router)
