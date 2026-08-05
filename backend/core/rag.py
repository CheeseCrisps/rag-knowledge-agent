import os
import sys
from typing import List

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

CHROMA_DB_DIR = "./chroma_db"

_embeddings = None
_vector_db = None


def get_vector_db():
    global _embeddings, _vector_db
    if _embeddings is None:
        print("--> [后台] 首次加载中文 Embedding 模型...")
        _embeddings = HuggingFaceEmbeddings(
            model_name="shibing624/text2vec-base-chinese"
        )
    if _vector_db is None:
        _vector_db = Chroma(
            persist_directory=CHROMA_DB_DIR,
            embedding_function=_embeddings
        )
    return _vector_db


async def process_and_store_pdf(file_path: str) -> int:
    loader = PyPDFLoader(file_path)
    documents = loader.load()
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = text_splitter.split_documents(documents)

    db = get_vector_db()
    db.add_documents(chunks)
    return len(chunks)


def query_relevant_context(query: str, top_k: int = 3) -> List[str]:
    db = get_vector_db()
    try:
        results = db.similarity_search(query, k=top_k)
        return [doc.page_content for doc in results]
    except Exception as e:
        print(f"检索提示: {e}")
        return []