from pymilvus import Collection, CollectionSchema, FieldSchema, DataType, utility
from db.base import has_collection, drop_collection
from utils.logging import setup_logger

logger = setup_logger("debug")

TENDER_COLLECTION_NAME = "tender_uploads"

def initialize_tender_collection() -> Collection:
    # drop_collection(TENDER_COLLECTION_NAME)
    if has_collection(TENDER_COLLECTION_NAME):
        collection = Collection(TENDER_COLLECTION_NAME)
        collection.load()
        return collection

    schema = CollectionSchema(fields=[
        FieldSchema(name="id", dtype=DataType.INT64, is_primary=True, auto_id=True),
        FieldSchema(name="tender_id", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="tender_name", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="tender_vector", dtype=DataType.FLOAT_VECTOR, dim=3072),
        FieldSchema(name="supplier_name", dtype=DataType.VARCHAR, max_length=512),
        FieldSchema(name="items", dtype=DataType.JSON),
        FieldSchema(name="created_at", dtype=DataType.VARCHAR, max_length=64),
        FieldSchema(name="updated_at", dtype=DataType.VARCHAR, max_length=64),
    ])

    collection = Collection(name=TENDER_COLLECTION_NAME, schema=schema)
    collection.create_index(
        field_name="tender_vector",
        index_params={"index_type": "FLAT", "metric_type": "L2", "params": {}}
    )
    collection.load()
    return collection

def insert_tender_supplier(
    collection: Collection,
    tender_id: str,
    tender_name: str,
    tender_vector: list,
    supplier_name: str,
    items: list[dict],
    created_at: str,
    updated_at: str
) -> None:
    try:
        collection.insert([
            [tender_id],
            [tender_name],
            [tender_vector],
            [supplier_name],
            [items],
            [created_at],
            [updated_at]
        ])
        logger.info(f"✅ Inserted supplier '{supplier_name}' for tender '{tender_name}'")
    except Exception as e:
        logger.error(f"❌ Failed to insert supplier '{supplier_name}': {e}")
