from __future__ import annotations

import logging
from pathlib import Path
from typing import Protocol
from uuid import UUID, uuid4

from sqlmodel import Session, select

from docforge.application.embeddings import SentenceTransformerEmbeddingService
from docforge.application.indexing import IndexingService
from docforge.application.parsers import PDFParser
from docforge.application.vector_store import ChromaVectorStore
from docforge.config import settings
from docforge.domain.models import Document, DocumentCreate, DocumentRead, DocumentStatus
from docforge.infrastructure.database import engine

logger = logging.getLogger("docforge")


class StorageProtocol(Protocol):
    def save(self, file_bytes: bytes, filename: str, document_id: UUID) -> str:
        ...


class DocumentServiceProtocol(Protocol):
    def upload_document(self, file_bytes: bytes, filename: str, content_type: str) -> DocumentRead:
        ...

    def list_documents(self) -> list[DocumentRead]:
        ...

    def get_document(self, document_id: str) -> DocumentRead | None:
        ...


class DocumentService:
    """Application service for creating and retrieving document records."""

    def __init__(
        self,
        storage: StorageProtocol,
        parser: PDFParser | None = None,
        indexing_service: IndexingService | None = None,
    ) -> None:
        self.storage = storage
        self.parser = parser or PDFParser()
        self.indexing_service = indexing_service or IndexingService(
            embedding_service=SentenceTransformerEmbeddingService(),
            vector_store=ChromaVectorStore(
                collection_name="docforge",
                persist_directory=str(Path(settings.storage_dir) / "chroma"),
            ),
        )

    def upload_document(self, file_bytes: bytes, filename: str, content_type: str) -> DocumentRead:
        if content_type != "application/pdf":
            raise ValueError("Only PDF files are supported")

        document_id = uuid4()
        stored_path = self.storage.save(file_bytes, filename, document_id)

        document = DocumentCreate(
            original_filename=filename,
            storage_path=stored_path,
            file_size_bytes=len(file_bytes),
            content_type=content_type,
            status=DocumentStatus.uploaded,
        )

        with Session(engine) as session:
            try:
                db_document = Document(**document.model_dump())
                db_document.id = document_id
                session.add(db_document)
                session.commit()
                session.refresh(db_document)
            except Exception:
                session.rollback()
                raise

        try:
            parsed_document = self.parser.parse(Path(stored_path))
            if self.indexing_service.index_document(parsed_document, str(document_id)):
                with Session(engine) as session:
                    db_document.status = DocumentStatus.indexed
                    session.add(db_document)
                    session.commit()
                    session.refresh(db_document)
            else:
                with Session(engine) as session:
                    db_document.status = DocumentStatus.uploaded
                    session.add(db_document)
                    session.commit()
                    session.refresh(db_document)
        except Exception as exc:
            logger.exception("Failed to parse and index uploaded document")
            with Session(engine) as session:
                db_document.status = DocumentStatus.failed
                session.add(db_document)
                session.commit()
                session.refresh(db_document)
            raise ValueError(str(exc)) from exc

        return DocumentRead.model_validate(db_document)

    def list_documents(self) -> list[DocumentRead]:
        with Session(engine) as session:
            documents = session.exec(select(Document)).all()
            return [DocumentRead.model_validate(document) for document in documents]

    def get_document(self, document_id: str) -> DocumentRead | None:
        with Session(engine) as session:
            try:
                document_uuid = UUID(document_id)
            except ValueError:
                return None

            document = session.get(Document, document_uuid)
            if document is None:
                return None
            return DocumentRead.model_validate(document)
