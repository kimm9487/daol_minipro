from fastapi import APIRouter
from .crud import crud_router
from .summarize import summarize_router
from .translate import translate_router
from .utility import utility_router
from .download import download_router

router = APIRouter(prefix="/api/documents", tags=["Documents"])

router.include_router(crud_router)
router.include_router(summarize_router)
router.include_router(translate_router)
router.include_router(utility_router)
router.include_router(download_router)
