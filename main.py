from typing import Optional
from fastapi import FastAPI
from pydantic import BaseModel, Field
from rag_guard import RAGShield, GuardResult

app = FastAPI(
    title="rag-guard Security Gateway",
    description="Zero-latency LLM & RAG security firewall for PII redaction, prompt injection defense, and hallucination checks.",
    version="1.0.0"
)

shield = RAGShield()

class EvaluateRequest(BaseModel):
    prompt: str = Field(..., min_length=1)
    context: Optional[str] = None
    response: Optional[str] = None

@app.get("/health", tags=["System"])
def health_check():
    return {"status": "healthy", "package": "rag-guard", "version": "1.0.0"}

@app.post("/evaluate", response_model=GuardResult, tags=["Guardrails"])
def evaluate_payload(payload: EvaluateRequest):
    return shield.evaluate(
        prompt=payload.prompt,
        context=payload.context,
        response=payload.response
    )
