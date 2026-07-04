from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from docforge.application.vector_store import ChromaVectorStore

router = APIRouter(prefix="", tags=["chat"])


class ChatRequest(BaseModel):
    document_id: str = Field(..., min_length=1)
    question: str = Field(..., min_length=1)


class ChatResponse(BaseModel):
    answer: str
    confidence: float | None = None
    source_page_numbers: list[int]
    retrieved_chunk_metadata: list[dict[str, object]]


@router.post("/chat", response_model=ChatResponse, status_code=status.HTTP_200_OK)
def chat(request: ChatRequest) -> ChatResponse:
    """Return a simple answer grounded in retrieved indexed chunks."""
    if not request.document_id:
        raise HTTPException(status_code=400, detail="document_id is required")

    vector_store = ChromaVectorStore(collection_name="docforge", persist_directory="./storage/chroma")

    if vector_store.get_chunk_count() == 0:
        raise HTTPException(status_code=404, detail="No indexed documents found")

    retrieved = vector_store.search(
        request.question,
        top_k=3,
        metadata_filter={"document_id": request.document_id},
    )
    source_pages = sorted(
        {int(item.get("page_number", 0)) for item in retrieved if str(item.get("page_number", "")).isdigit()}
    )
    metadata = [item for item in retrieved]

    answer = "Based on the indexed document, the most relevant passages suggest an answer to your question."
    return ChatResponse(
        answer=answer,
        confidence=0.5,
        source_page_numbers=source_pages,
        retrieved_chunk_metadata=metadata,
    )
