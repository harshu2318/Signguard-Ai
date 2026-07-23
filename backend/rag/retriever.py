"""
SignGuard AI — ChromaDB Retriever
====================================
Loads the persisted ChromaDB vector store and returns a configured retriever
that fetches the top-4 most relevant chunks for each query.
"""
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.vectorstores import VectorStoreRetriever

from config import CHROMA_DIR, EMBEDDING_MODEL

COLLECTION_NAME = "signguard_rag"


def get_retriever() -> VectorStoreRetriever:
    """
    Load ChromaDB from disk and return a similarity retriever.

    Returns:
        A LangChain VectorStoreRetriever (top-4 chunks per query).

    Raises:
        FileNotFoundError: if the vector database has not been built yet.
    """
    chroma_db_file = CHROMA_DIR / "chroma.sqlite3"
    if not chroma_db_file.exists():
        raise FileNotFoundError(
            f"ChromaDB not found at {CHROMA_DIR}.\n"
            "Please build the vector database first:\n"
            "  cd backend\n"
            "  python rag/build_vector_db.py"
        )

    embeddings = HuggingFaceEmbeddings(
        model_name   = EMBEDDING_MODEL,
        model_kwargs = {"device": "cpu"},
        encode_kwargs= {"normalize_embeddings": True},
    )

    vectorstore = Chroma(
        persist_directory = str(CHROMA_DIR),
        embedding_function= embeddings,
        collection_name   = COLLECTION_NAME,
    )

    return vectorstore.as_retriever(
        search_type  = "similarity",
        search_kwargs= {"k": 4},
    )
