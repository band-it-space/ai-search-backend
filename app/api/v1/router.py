from fastapi import APIRouter
from api.v1.endpoints.upload import router as upload_router
from api.v1.endpoints.search import router as search_router
from api.v1.endpoints.remove_all_collection import router as remove_router
from api.v1.endpoints.upload_tender import router as upload_tender_router
from api.v1.endpoints.tender import router as tender_router


api_router = APIRouter()
api_router.include_router(upload_router, prefix="/upload", tags=["upload"])
api_router.include_router(search_router, prefix="/search", tags=["search"])
api_router.include_router(remove_router, prefix="/remove_all", tags=["milvus"])
api_router.include_router(upload_tender_router, prefix="/upload-tender", tags=["tender"])
api_router.include_router(tender_router, tags=["tender"])
