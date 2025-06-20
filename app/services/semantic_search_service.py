from typing import List
import numpy as np
from fastapi import Request
from db.base import openai_embeddings, COLLECTION_NAME
from db.goods_collection import initialize_goods_collection
from utils.logging import setup_logger

logger = setup_logger("debug")

collection = initialize_goods_collection()

def search_by_queries(request: Request, queries: List[str], limit: int = 10) -> List[List[dict]]:
    embeddings = openai_embeddings.embed_documents(queries)
    np_embeddings = [np.array(vec, dtype=np.float32).tolist() for vec in embeddings]

    results = collection.search(
        data=np_embeddings,
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"search_list": 100}},
        limit=limit,
        output_fields=["text", "name", "costs", "costs_NDS", "tovar_name", "name_tovar_1C", "date_prihod"]
    )

    logger.info(f"results: {results}")

    all_items = []
    for hits in results:
        unique_suppliers = {}
        for hit in hits:
            if hit.distance >= 0.6:
                logger.info(f"HIT: {hit.entity.get('tovar_name')} — score: {hit.distance}")

                name = hit.entity.get("name")
                if name not in unique_suppliers:
                    unique_suppliers[name] = {
                        "text": hit.entity.get("text"),
                        "score": hit.distance,
                        "name": name,
                        "costs": hit.entity.get("costs"),
                        "costs_NDS": hit.entity.get("costs_NDS"),
                        "tovar_name": hit.entity.get("tovar_name"),
                        "name_tovar_1C": hit.entity.get("name_tovar_1C"),
                        "date_prihod": hit.entity.get("date_prihod"),
                    }
        all_items.append(list(unique_suppliers.values()))
    return all_items
