import io
import uuid
import docx2txt
from typing import Dict
import pandas as pd
from fastapi import Request
from datetime import datetime
from utils.logging import setup_logger
from services.semantic_search_service import search_by_queries
from db.tender_collection import initialize_tender_collection, insert_tender_supplier
from db.base import openai_embeddings

logger = setup_logger("debug")

def extract_lines_from_docx(content: bytes) -> list[str]:
    text = docx2txt.process(io.BytesIO(content))
    return [line.strip() for line in text.splitlines() if line.strip()]

def upload_tender_file(request: Request, filename: str, content: bytes, tender_name: str) -> Dict:
    try:
        df = pd.read_excel(io.BytesIO(content))
        if "tovar_name" not in df.columns or "count" not in df.columns:
            return {"error": "Expected columns 'tovar_name' and 'count' not found."}

        lines = df.to_dict(orient="records")

        if not lines:
            return {"error": "No lines extracted from document."}

        collection = initialize_tender_collection()
        tender_vector = openai_embeddings.embed_query(tender_name)

        queries = [entry["tovar_name"] for entry in lines]
        counts_map = {entry["tovar_name"]: entry["count"] for entry in lines}
        all_results = search_by_queries(request, queries, limit=50)


        suppliers_map = {}

        tender_id = str(uuid.uuid4())

        for query, result in zip(queries, all_results):
            for item in result:
                supplier = item["name"]
                item["count"] = counts_map.get(query, 1)
                if supplier not in suppliers_map:
                    suppliers_map[supplier] = []
                suppliers_map[supplier].append(item)

        for supplier, items in suppliers_map.items():
            now = datetime.utcnow().isoformat()
            insert_tender_supplier(
                collection=collection,
                tender_id=tender_id,
                tender_name=tender_name,
                tender_vector=tender_vector,
                supplier_name=supplier,
                items=items,
                created_at=now,
                updated_at=now
            )


        return {
            "message": f"Tender '{tender_name}' uploaded with {len(suppliers_map)} suppliers.",
            "supplier_count": len(suppliers_map)
        }

    except Exception as e:
        logger.error(f"Error processing file '{filename}': {e}")
        return {"error": str(e)}
