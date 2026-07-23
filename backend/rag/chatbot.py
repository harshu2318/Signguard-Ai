"""
SignGuard AI - RAG Chatbot
============================
Uses LangChain Expression Language (LCEL) pipeline to answer questions about
signature verification using ONLY the retrieved research paper context.

Compatible with langchain >= 1.x (no deprecated langchain.chains module).
"""
from typing import Optional

from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

import config
from rag.retriever import get_retriever
from rag.prompt_template import build_prompt

# Module-level retriever (initialised once at startup)
_retriever = None


def initialize_rag() -> None:
    """
    Load the ChromaDB retriever at application startup.
    Called from app.py lifespan so it runs once when the server starts.
    Prints a warning (instead of crashing) if the DB is not ready yet.
    """
    global _retriever
    try:
        _retriever = get_retriever()
        print("RAG retriever initialised successfully.")
    except FileNotFoundError as exc:
        print(f"WARNING: RAG not available: {exc}")
        print("   Run: cd backend && python rag/build_vector_db.py")
        _retriever = None


def _format_docs(docs) -> str:
    """Concatenate retrieved document chunks into a single context string."""
    return "\n\n".join(doc.page_content for doc in docs)


def get_answer(
    question:   str,
    prediction: Optional[str] = None,
    confidence: Optional[int] = None,
) -> str:
    """
    Answer a user question using Retrieval-Augmented Generation (LCEL pipeline).

    Args:
        question:   The user's natural-language question.
        prediction: Optional verdict from the ML model ("Genuine" / "Forged").
        confidence: Optional confidence score (0-100).

    Returns:
        Answer string from the LLM grounded in the research paper.
    """
    # Guard: RAG not initialised
    if _retriever is None:
        return (
            "The knowledge base is not available. "
            "Please run the following command and restart the server:\n"
            "  cd backend && python rag/build_vector_db.py"
        )

    # Guard: missing API key
    if not config.GROQ_API_KEY and not config.HUGGINGFACEHUB_API_TOKEN:
        return (
            "Neither GROQ_API_KEY nor HUGGINGFACEHUB_API_TOKEN is configured. "
            "Please add one of these keys to backend/.env and restart the server."
        )

    # Build LLM
    if config.GROQ_API_KEY:
        from langchain_groq import ChatGroq
        llm = ChatGroq(
            api_key    = config.GROQ_API_KEY,
            model      = config.GROQ_MODEL,
            temperature= 0.1,
            max_tokens = 1024,
        )
    else:
        from langchain_huggingface import HuggingFaceEndpoint, ChatHuggingFace
        raw_llm = HuggingFaceEndpoint(
            repo_id                  = config.HF_MODEL,
            huggingfacehub_api_token = config.HUGGINGFACEHUB_API_TOKEN,
            temperature              = 0.1,
            max_new_tokens           = 1024,
        )
        llm = ChatHuggingFace(llm=raw_llm)

    # Build context-aware prompt
    prompt = build_prompt(prediction=prediction, confidence=confidence)

    # LCEL chain: retriever -> format docs -> prompt -> LLM -> parse output
    rag_chain = (
        {
            "context": _retriever | _format_docs,
            "input":   RunnablePassthrough(),
        }
        | prompt
        | llm
        | StrOutputParser()
    )

    try:
        answer = rag_chain.invoke(question).strip()
        if not answer:
            return "I couldn't find that information in the research paper."
        return answer
    except Exception as exc:
        return f"An error occurred while generating the answer: {exc}"
