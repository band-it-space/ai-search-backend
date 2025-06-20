from fastapi import APIRouter
from services.vector_service import remove_all_collection

router = APIRouter()

@router.delete("/")
def remove_collection_route():
    try:
        return remove_all_collection()
    except Exception as e:
        return {"error": str(e)}
