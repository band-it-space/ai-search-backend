import time
from typing import List
import numpy as np
from langchain_community.embeddings import OpenAIEmbeddings
from utils.convert import parse_float
from utils.logging import setup_logger
from db.base import openai_embeddings, OPENAI_API_KEY, ASSISTANT_ID, COLLECTION_NAME, MILVUS_HOST, MILVUS_PORT, drop_collection
from db.goods_collection import initialize_goods_collection, record_exists
from fastapi import Request

logger = setup_logger("debug")

collection = initialize_goods_collection()

def remove_all_collection():
    drop_collection(COLLECTION_NAME)
    initialize_goods_collection()
    return {"message": f"Collection '{COLLECTION_NAME}' removed (if existed)."}

def store_product_records(records: List[dict], batch_size: int = 1000):

    new_records = []
    for record in records:
        tovar_name = str(record.get("tovar_name", ""))
        name_1c = str(record.get("name_tovar_1C", ""))
        if not record_exists(collection, tovar_name, name_1c):
            new_records.append(record)

    if not new_records:
        # logger.info("No new unique records to insert.")
        return []

    for i in range(0, len(new_records), batch_size):
        batch = new_records[i:i + batch_size]
        texts = [
            f"{record.get('tovar_name', '')} {record.get('name_tovar_1C', '')} {record.get('name', '')}"
            for record in batch
        ]
        embeddings = openai_embeddings.embed_documents(texts)

        entities = [
            texts,
            embeddings,
            [str(record.get("date_prihod", "")) for record in batch],
            [parse_float(record.get("costs", 0)) for record in batch],
            [parse_float(record.get("costs_NDS", 0)) for record in batch],
            [str(record.get("name", "")) for record in batch],
            [str(record.get("tovar_name", "")) for record in batch],
            [str(record.get("name_tovar_1C", "")) for record in batch],
        ]

        collection.insert(entities)
        collection.load()
    return new_records


def search_similar_products(request: Request, query: str, limit: int = 10):
    assistant_manager = request.app.state.assistant_manager

    query_embedding: OpenAIEmbeddings = openai_embeddings.embed_query(query)
    query_embedding = np.array(query_embedding, dtype=np.float32).tolist()
    logger.info(f'Query:{query}')
    results = collection.search(
        data=[query_embedding],
        anns_field="embedding",
        param={"metric_type": "COSINE", "params": {"search_list": 100}},
        limit=limit,
        output_fields=["text", "name", "costs", "costs_NDS", "tovar_name", "name_tovar_1C", "date_prihod"]
    )
    logger.info(f'Results:{results}')
    unique_suppliers = {}
    for hits in results:
        for hit in hits:
            logger.info(f'distance:{hit.distance}')
            if hit.distance >= 0.5:
                supplier_name = hit.entity.get("name")
                if supplier_name not in unique_suppliers:
                    unique_suppliers[supplier_name] = {
                        "text": hit.entity.get("text"),
                        "score": hit.distance,
                        "name": supplier_name,
                        "costs": hit.entity.get("costs"),
                        "costs_NDS": hit.entity.get("costs_NDS"),
                        "tovar_name": hit.entity.get("tovar_name"),
                        "name_tovar_1C": hit.entity.get("name_tovar_1C"),
                        "date_prihod": hit.entity.get("date_prihod"),
                    }

        items = list(unique_suppliers.values())
        logger.info(f'Items:{items}')

        items_text = "\n".join(
            f"- Назва: {item['tovar_name']}\n  1С: {item['name_tovar_1C']}\n Постачальник: {item['name']}\n"
            for item in items
        )

        task_id = f"ext_relevant_{int(time.time())}"
        assistant_manager.add_task(
            task_id=task_id,
            lines=[
                f"query: {query}",
                f"products: {items_text}"
            ],
            function_name="extracting_relevant_products",
        )

        result = None
        # while result is None or result.get("response") is None:
        #     result = assistant_manager.get_task_result(task_id)
        #     time.sleep(1)

        logger.info(f"app.services.vector_service.py | result: {result}")

        # relevant_names = result["response"][0].get("relevant_products", [])

        # items = [item for item in items if item["tovar_name"] in relevant_names]

    return items
