"""
SignGuard AI — Central Configuration
Loads all paths, environment variables, and model settings from one place.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from the backend directory
load_dotenv(Path(__file__).parent / ".env")

# ─── Directory Paths ──────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent           # backend/
ML_DIR        = BASE_DIR / "ml"                 # backend/ml/
KNOWLEDGE_DIR = BASE_DIR / "knowledge"          # backend/knowledge/
CHROMA_DIR    = BASE_DIR / "chroma_db"          # backend/chroma_db/
UPLOADS_DIR   = BASE_DIR / "uploads"            # backend/uploads/

# ─── File Paths ───────────────────────────────────────────────────────────────
MODEL_PATH = ML_DIR / "model.pkl"
PDF_PATH   = KNOWLEDGE_DIR / "SignGuard_Research_Paper.pdf"

# ─── API Keys ─────────────────────────────────────────────────────────────────
GROQ_API_KEY             = os.getenv("GROQ_API_KEY", "")
HUGGINGFACEHUB_API_TOKEN = os.getenv("HUGGINGFACEHUB_API_TOKEN", "") or os.getenv("HF_TOKEN", "")

if HUGGINGFACEHUB_API_TOKEN:
    os.environ["HF_TOKEN"] = HUGGINGFACEHUB_API_TOKEN
    os.environ["HUGGINGFACEHUB_API_TOKEN"] = HUGGINGFACEHUB_API_TOKEN

# ─── Model / RAG Settings ─────────────────────────────────────────────────────
GROQ_MODEL      = "llama-3.1-8b-instant"
HF_MODEL        = "Qwen/Qwen2.5-7B-Instruct"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# ─── Ensure required directories exist at import time ─────────────────────────
UPLOADS_DIR.mkdir(parents=True, exist_ok=True)
KNOWLEDGE_DIR.mkdir(parents=True, exist_ok=True)
CHROMA_DIR.mkdir(parents=True, exist_ok=True)
