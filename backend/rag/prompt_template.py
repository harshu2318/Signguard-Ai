"""
SignGuard AI — RAG Prompt Template
=====================================
Builds a context-aware ChatPromptTemplate for the LangChain retrieval chain.

The system prompt instructs the LLM to answer ONLY from the research paper.
If prediction context is provided (e.g. "Forged, 94%"), it is injected so
the chatbot can explain specific predictions.
"""
from typing import Optional
from langchain_core.prompts import ChatPromptTemplate

# ─── Base system instruction ──────────────────────────────────────────────────
_SYSTEM_BASE = """\
You are SignGuard AI Assistant, an expert in handwritten signature verification \
and forensic document analysis.

Your knowledge comes EXCLUSIVELY from the provided research paper context below.
- Answer questions clearly, concisely, and professionally.
- If the answer is NOT found in the context, respond with EXACTLY:
  "I couldn't find that information in the research paper."
- Do NOT make up, infer, or hallucinate information beyond the context.
- Do NOT reference external sources, papers, or tools not mentioned in the context.
{prediction_block}
Context from the research paper:
{{context}}\
"""

# ─── Prediction context block (injected when a prediction exists) ─────────────
_PREDICTION_BLOCK = """\

Current Signature Analysis:
  - Verdict     : {prediction}
  - Confidence  : {confidence}%

When the user asks questions like "Why is this {prediction_lower}?" or \
"Explain this prediction", incorporate the above verdict and confidence \
into your answer along with insights from the research paper context.\

"""


def build_prompt(
    prediction: Optional[str] = None,
    confidence: Optional[int] = None,
) -> ChatPromptTemplate:
    """
    Build a ChatPromptTemplate.

    Args:
        prediction: "Genuine" or "Forged" from the latest ML prediction.
        confidence: Integer confidence score (0–100).

    Returns:
        A LangChain ChatPromptTemplate ready for create_stuff_documents_chain.
    """
    if prediction and confidence is not None:
        pred_block = _PREDICTION_BLOCK.format(
            prediction       = prediction,
            confidence       = confidence,
            prediction_lower = prediction.lower(),
        )
    else:
        pred_block = "\n"

    system_prompt = _SYSTEM_BASE.replace("{prediction_block}", pred_block)

    return ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        ("human",  "{input}"),
    ])
