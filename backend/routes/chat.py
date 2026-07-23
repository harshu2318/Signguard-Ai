"""
SignGuard AI — Chat Route
===========================
POST /chat
    Accepts a user question (and optional prediction context),
    passes it through the RAG chatbot, and returns the answer.
"""
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from rag.chatbot import get_answer

router = APIRouter(tags=["Chat"])


class ChatRequest(BaseModel):
    question:   str            = Field(..., min_length=1,
                                       description="User's question about signature verification")
    prediction: Optional[str]  = Field(None,
                                       description="Latest prediction: 'Genuine' or 'Forged'")
    confidence: Optional[int]  = Field(None, ge=0, le=100,
                                       description="Confidence score (0–100)")


class ChatResponse(BaseModel):
    answer: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Answer a question using Retrieval-Augmented Generation.

    Optionally pass `prediction` and `confidence` so the chatbot
    can give context-aware answers like *"Why is this forged?"*.

    Returns:
    ```json
    { "answer": "..." }
    ```
    """
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty.")

    try:
        answer = get_answer(
            question   = request.question,
            prediction = request.prediction,
            confidence = request.confidence,
        )
        return ChatResponse(answer=answer)

    except Exception as exc:
        raise HTTPException(status_code=500,
                            detail=f"Chat error: {exc}") from exc
