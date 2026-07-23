"""
SignGuard AI — Build Vector Database
=======================================
Run this ONCE after placing the PDF in backend/knowledge/.

Usage
-----
    cd backend
    python rag/build_vector_db.py

What it does
------------
    1. Loads SignGuard_Research_Paper.pdf with PyPDFLoader
    2. Splits text into 800-token chunks (100-token overlap) with
       RecursiveCharacterTextSplitter
    3. Generates embeddings using sentence-transformers/all-MiniLM-L6-v2
       (runs locally — no API key required)
    4. Persists the vector store to backend/chroma_db/
"""
import sys
from pathlib import Path

# Ensure backend root is on sys.path when run as a script
sys.path.insert(0, str(Path(__file__).parent.parent))

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma

from config import PDF_PATH, CHROMA_DIR, EMBEDDING_MODEL

COLLECTION_NAME = "signguard_rag"


def build_vector_db() -> None:
    """Load PDF → chunk → embed → persist to ChromaDB."""

    print("======================================")
    print("  SignGuard AI - Building Vector DB")
    print("======================================\n")

    # ── Validate PDF ──────────────────────────────────────────────────────────
    if not PDF_PATH.exists():
        print(f"❌ PDF not found: {PDF_PATH}")
        print(
            "\nFix: copy your research paper to:\n"
            f"  {PDF_PATH}\n"
            "and re-run this script."
        )
        sys.exit(1)

    # ── Load PDF ──────────────────────────────────────────────────────────────
    print(f"📄 Loading PDF: {PDF_PATH.name}")
    loader    = PyPDFLoader(str(PDF_PATH))
    documents = loader.load()
    print(f"   Loaded {len(documents)} page(s)")

    # -- Chunk ------------------------------------------------------------------
    print("\nSplitting into chunks...")
    splitter = RecursiveCharacterTextSplitter(
        chunk_size    = 800,
        chunk_overlap = 100,
        separators    = ["\n\n", "\n", ".", " ", ""],
    )
    chunks = splitter.split_documents(documents)
    print(f"   Created {len(chunks)} chunks")

    # -- Embed ------------------------------------------------------------------
    print(f"\nLoading embedding model: {EMBEDDING_MODEL}")
    print("   (First run downloads ~90 MB - please wait...)")
    embeddings = HuggingFaceEmbeddings(
        model_name   = EMBEDDING_MODEL,
        model_kwargs = {"device": "cpu"},
        encode_kwargs= {"normalize_embeddings": True},
    )

    # -- Persist to ChromaDB ----------------------------------------------------
    CHROMA_DIR.mkdir(parents=True, exist_ok=True)
    print(f"\nStoring in ChromaDB: {CHROMA_DIR}")

    Chroma.from_documents(
        documents        = chunks,
        embedding        = embeddings,
        persist_directory= str(CHROMA_DIR),
        collection_name  = COLLECTION_NAME,
    )

    print(f"\nVector database built successfully!")
    print(f"   Collection : {COLLECTION_NAME}")
    print(f"   Chunks     : {len(chunks)}")
    print("\nYou can now start the FastAPI backend.")


if __name__ == "__main__":
    build_vector_db()
