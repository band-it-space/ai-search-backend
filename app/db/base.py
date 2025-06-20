import os
from pymilvus import connections, utility
from langchain_community.embeddings import OpenAIEmbeddings
from langchain_community.chat_models import ChatOpenAI
import openai
from utils.logging import setup_logger

logger = setup_logger("debug")

MILVUS_HOST = os.getenv("MILVUS_HOST", "milvus")
MILVUS_PORT = os.getenv("MILVUS_PORT", "19530")
COLLECTION_NAME = os.getenv("MILVUS_COLLECTION", "goods_import")
EMBEDDING_DIM = int(os.getenv("EMBEDDING_DIM", 3072))
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ASSISTANT_ID = os.getenv("ASSISTANT_ID")

connections.connect(host=MILVUS_HOST, port=MILVUS_PORT)
openai.api_key = OPENAI_API_KEY

openai_embeddings: OpenAIEmbeddings = OpenAIEmbeddings(model="text-embedding-3-large", openai_api_key=OPENAI_API_KEY)
openai_gpt = ChatOpenAI(model="gpt-4o", temperature=0, openai_api_key=OPENAI_API_KEY)

def has_collection(name: str) -> bool:
    return utility.has_collection(name)

def drop_collection(name: str):
    if has_collection(name):
        utility.drop_collection(name)
        logger.info(f"Collection '{name}' was dropped.")
