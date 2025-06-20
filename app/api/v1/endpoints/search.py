from fastapi import APIRouter, Query, Request
from services.vector_service import search_similar_products

router = APIRouter()

@router.get("/")
def search(request: Request, query: str = Query(..., min_length=1), limit: int = 5):
    try:
        results = search_similar_products(request, query, limit=limit)
        return {"query": query, "results": results}
    except Exception as error:
        return {"error": str(error)}
