from __future__ import annotations

from datetime import UTC, datetime
from enum import StrEnum
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"


class Document(SQLModel, table=True):
    id: UUID | None = Field(default_factory=uuid4, primary_key=True)
    original_filename: str
    storage_path: str
    file_size_bytes: int
    content_type: str
    status: DocumentStatus = Field(default=DocumentStatus.uploaded)
    uploaded_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    checksum: str | None = None


class DocumentRead(SQLModel):
    id: UUID
    original_filename: str
    storage_path: str
    file_size_bytes: int
    content_type: str
    status: DocumentStatus
    uploaded_at: datetime
    updated_at: datetime
    checksum: str | None = None


class DocumentCreate(SQLModel):
    original_filename: str
    storage_path: str
    file_size_bytes: int
    content_type: str
    status: DocumentStatus = DocumentStatus.uploaded
    checksum: str | None = None
