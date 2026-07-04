from __future__ import annotations

from pathlib import Path
from uuid import UUID

from docforge.config import settings


class FileStorage:
    def __init__(self, storage_dir: str | None = None) -> None:
        self.storage_dir = Path(storage_dir or settings.storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)

    def save(self, file_bytes: bytes, filename: str, document_id: UUID) -> str:
        safe_name = Path(filename).name
        destination = self.storage_dir / f"{document_id}-{safe_name}"
        destination.write_bytes(file_bytes)
        return str(destination)
