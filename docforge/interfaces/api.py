from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, File, HTTPException, UploadFile, status

from docforge.application.embeddings import SentenceTransformerEmbeddingService
from docforge.application.indexing import IndexingService
from docforge.application.parsers import PDFParser
from docforge.application.services import DocumentService
from docforge.application.vector_store import ChromaVectorStore
from docforge.config import settings
from docforge.domain.models import DocumentRead
from docforge.infrastructure.database import create_db_and_tables
from docforge.infrastructure.storage import FileStorage

logger = logging.getLogger("docforge")


def get_document_service() -> DocumentService:
    """Build a document service instance from the configured storage backend."""
    storage = FileStorage(settings.storage_dir)
    vector_store = ChromaVectorStore(
        collection_name="docforge",
        persist_directory=str(Path(settings.storage_dir) / "chroma"),
    )
    indexing_service = IndexingService(
        embedding_service=SentenceTransformerEmbeddingService(),
        vector_store=vector_store,
    )
    return DocumentService(storage, parser=PDFParser(), indexing_service=indexing_service)


def register_routes(app: FastAPI) -> None:
    @app.post("/documents/upload", response_model=DocumentRead, status_code=status.HTTP_201_CREATED)
    async def upload_document(
        file: Annotated[UploadFile, File(...)],
        service: DocumentService = Depends(get_document_service),
    ) -> DocumentRead:
        if file.filename is None:
            raise HTTPException(status_code=400, detail="A file name is required")

        if not file.filename.lower().endswith(".pdf"):
            logger.warning("Rejected unsupported upload: %s", file.filename)
            raise HTTPException(status_code=415, detail="Only PDF files are supported")

        try:
            contents = await file.read()
        except Exception as exc:  # pragma: no cover - defensive path
            logger.exception("Failed to read uploaded file")
            raise HTTPException(status_code=400, detail="Could not read uploaded file") from exc

        if not contents:
            raise HTTPException(status_code=400, detail="Uploaded file is empty")

        try:
            document = service.upload_document(
                contents,
                file.filename,
                file.content_type or "application/pdf",
            )
        except ValueError as exc:
            logger.warning("Upload rejected: %s", exc)
            raise HTTPException(status_code=415, detail=str(exc)) from exc

        logger.info("Document uploaded successfully", extra={"document_id": str(document.id)})
        return document

    @app.get("/documents/{document_id}", response_model=DocumentRead)
    async def get_document(
        document_id: str,
        service: DocumentService = Depends(get_document_service),
    ) -> DocumentRead:
        document = service.get_document(document_id)
        if document is None:
            raise HTTPException(status_code=404, detail="Document not found")
        return document

    @app.get("/documents", response_model=list[DocumentRead])
    async def list_documents(
        service: DocumentService = Depends(get_document_service),
    ) -> list[DocumentRead]:
        return service.list_documents()


create_db_and_tables()
