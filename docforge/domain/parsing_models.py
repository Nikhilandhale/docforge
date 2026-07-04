from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class Chunk:
    text: str
    page_number: int
    start_char: int
    end_char: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class ParsedDocument:
    document_id: str | None
    metadata: dict[str, Any]
    page_count: int
    chunks: list[Chunk]
    warnings: list[str] = field(default_factory=list)
