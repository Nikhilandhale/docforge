from __future__ import annotations

from pathlib import Path
from typing import Protocol

import fitz

from docforge.domain.parsing_models import Chunk, ParsedDocument


class Parser(Protocol):
    def parse(self, file_path: Path) -> ParsedDocument: ...


class PDFParser:
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50) -> None:
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def parse(self, file_path: Path) -> ParsedDocument:
        try:
            document = fitz.open(file_path)
        except (RuntimeError, ValueError, fitz.FileNotFoundError) as exc:
            return ParsedDocument(
                document_id=None,
                metadata={"error": str(exc)},
                page_count=0,
                chunks=[],
                warnings=[f"Unable to open PDF: {exc}"],
            )

        chunks: list[Chunk] = []
        warnings: list[str] = []

        try:
            metadata = {
                "title": document.metadata.get("title", "") or "",
                "author": document.metadata.get("author", "") or "",
                "subject": document.metadata.get("subject", "") or "",
                "keywords": document.metadata.get("keywords", "") or "",
                "creation_date": document.metadata.get("creationDate", "") or "",
                "modification_date": document.metadata.get("modDate", "") or "",
            }

            page_count = document.page_count

            for page_number in range(page_count):
                page = document.load_page(page_number)
                text = page.get_text("text")
                if not text or not text.strip():
                    continue

                page_chunks = self._chunk_text(text, page_number)
                chunks.extend(page_chunks)

            if not chunks:
                warnings.append("No extractable text found in PDF")
        except (RuntimeError, ValueError) as exc:
            warnings.append(f"Failed while parsing PDF: {exc}")
        finally:
            document.close()

        return ParsedDocument(
            document_id=None,
            metadata=metadata,
            page_count=page_count,
            chunks=chunks,
            warnings=warnings,
        )

    def _chunk_text(self, text: str, page_number: int) -> list[Chunk]:
        normalized_text = text.strip()
        if not normalized_text:
            return []

        chunk_size = max(1, self.chunk_size)
        overlap = max(0, min(self.chunk_overlap, chunk_size - 1))
        chunks: list[Chunk] = []
        start = 0
        index = 0

        while start < len(normalized_text):
            end = min(len(normalized_text), start + chunk_size)
            chunk_text = normalized_text[start:end]
            chunks.append(
                Chunk(
                    text=chunk_text,
                    page_number=page_number + 1,
                    start_char=start,
                    end_char=end,
                    metadata={"page_number": page_number + 1},
                )
            )
            if end >= len(normalized_text):
                break
            start = max(0, end - overlap)
            index += 1

        return chunks


class ParserRegistry:
    def __init__(self) -> None:
        self._parsers: dict[str, Parser] = {}

    def register(self, content_type: str, parser: Parser) -> None:
        self._parsers[content_type] = parser

    def get_parser(self, content_type: str) -> Parser | None:
        return self._parsers.get(content_type)
