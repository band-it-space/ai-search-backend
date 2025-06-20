from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, utility
from db.base import has_collection, drop_collection, COLLECTION_NAME, EMBEDDING_DIM, logger

def initialize_goods_collection() -> Collection:
    if has_collection(COLLECTION_NAME):
        collection = Collection(COLLECTION_NAME)
        collection.load()
        logger.info(f"Using existing collection: {COLLECTION_NAME}")
        return collection
    
    # if utility.has_collection(COLLECTION_NAME):
    #     utility.drop_collection(COLLECTION_NAME)

    schema = CollectionSchema(fields=[
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="text", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="embedding", dtype=DataType.FLOAT_VECTOR, dim=EMBEDDING_DIM),
        FieldSchema(name="date_prihod", dtype=DataType.VARCHAR, max_length=128),
        FieldSchema(name="costs", dtype=DataType.FLOAT),
        FieldSchema(name="costs_NDS", dtype=DataType.FLOAT),
        FieldSchema(name="name", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="tovar_name", dtype=DataType.VARCHAR, max_length=2048),
        FieldSchema(name="name_tovar_1C", dtype=DataType.VARCHAR, max_length=2048),
    ])


    collection = Collection(name=COLLECTION_NAME, schema=schema)
    collection.create_index(field_name="embedding", index_params={
        "metric_type": "COSINE",
        "index_type": "DISKANN",
        "params": {"search_list": 100}
    })
    collection.load()
    logger.info(f"Created and loaded collection: {COLLECTION_NAME}")

    return collection


def escape_quotes(value: str) -> str:
    return value.replace('"', '\\"')


def record_exists(collection: Collection, tovar_name: str, name_tovar_1C: str) -> bool:
    expr = f'tovar_name == "{escape_quotes(tovar_name)}" and name_tovar_1C == "{escape_quotes(name_tovar_1C)}"'
    results = collection.query(expr, output_fields=["tovar_name"], limit=1)
    return bool(results)
