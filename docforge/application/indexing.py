from __future__ import annotations

from typing import Protocol

from docforge.application.embeddings import EmbeddingService
from docforge.application.vector_store import VectorStore
from docforge.domain.parsing_models import ParsedDocument


class IndexingService:
    def __init__(self, embedding_service: EmbeddingService, vector_store: VectorStore) -> None:
        self.embedding_service = embedding_service
        self.vector_store = vector_store

    def index_document(self, parsed_document: ParsedDocument, document_id: str) -> bool:
        if not parsed_document.chunks:
            return False

        texts = [chunk.text for chunk in parsed_document.chunks]
        embeddings = self.embedding_service.embed(texts)

        documents: list[dict[str, object]] = []
        for index, chunk in enumerate(parsed_document.chunks):
            flattened_metadata: dict[str, object] = {}
            for key, value in chunk.metadata.items():
                if isinstance(value, (str, int, float, bool)) or value is None:
                    flattened_metadata[key] = value

            documents.append(
                {
                    "text": chunk.text,
                    "document_id": document_id,
                    "page_number": chunk.page_number,
                    "chunk_index": index,
                    **flattened_metadata,
                }
            )

        self.vector_store.add_documents(documents, embeddings)
        return True
