"""
SignGuard AI — FastAPI Application Entry Point
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routes.upload import router as upload_router
from routes.chat import router as chat_router
from rag.chatbot import initialize_rag


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Run startup tasks: initialize the RAG retriever once."""
    initialize_rag()
    yield
    # (add shutdown cleanup here if needed)
    # "If you want something to happen when the application starts, put it inside a lifespan function."


app = FastAPI(
    title="SignGuard AI API",
    description="AI-powered Handwritten Signature Verification with RAG",
    version="1.0.0",
    lifespan=lifespan,
)

# ─── CORS ─────────────────────────────────────────────────────────────────────
# Allow requests from the Vite dev server (port 5173).
# Update origins for production deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,    
    # "It's okay to send cookies and authentication information to my backend."
    allow_methods=["*"],
    # "Allow every HTTP method."
    allow_headers=["*"],
)

# ─── Routes ───────────────────────────────────────────────────────────────────
app.include_router(upload_router)
app.include_router(chat_router)


@app.get("/", tags=["Health"])
def health_check():
    return {"status": "ok", "message": "SignGuard AI API is running 🔏"}
# used to check the backend is alive or not 