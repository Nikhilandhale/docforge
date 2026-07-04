import asyncio
from pathlib import Path
from types import SimpleNamespace

import fitz

from docforge.application.parsers import ParserRegistry, PDFParser
from docforge.domain.parsing_models import ParsedDocument
from docforge.interfaces.pdf_routes import parse_pdf


def test_pdf_parser_extracts_metadata_and_chunks(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Alpha beta gamma\n\nDelta epsilon zeta")
    document.save(pdf_path)
    document.close()

    parser = PDFParser(chunk_size=20, chunk_overlap=0)
    parsed = parser.parse(pdf_path)

    assert isinstance(parsed, ParsedDocument)
    assert parsed.metadata["title"] == ""
    assert parsed.page_count == 1
    assert len(parsed.chunks) >= 1
    assert parsed.chunks[0].page_number == 1


def test_parser_registry_registers_pdf_parser() -> None:
    registry = ParserRegistry()
    registry.register("application/pdf", PDFParser())

    parser = registry.get_parser("application/pdf")
    assert parser is not None
    assert isinstance(parser, PDFParser)


def test_parse_pdf_closes_temp_file_before_parsing(monkeypatch: object) -> None:
    class FakeTemporaryFile:
        def __init__(self, *args: object, **kwargs: object) -> None:
            self.name = "temp.pdf"
            self.closed = False

        def __enter__(self) -> "FakeTemporaryFile":
            return self

        def __exit__(self, exc_type: object, exc: object, tb: object) -> bool:
            self.close()
            return False

        def write(self, content: bytes) -> None:
            self._content = content

        def flush(self) -> None:
            return None

        def close(self) -> None:
            self.closed = True

    class FakeParser:
        def __init__(self, temp_file: FakeTemporaryFile) -> None:
            self.temp_file = temp_file

        def parse(self, file_path: Path) -> ParsedDocument:
            assert self.temp_file.closed is True
            return ParsedDocument(document_id=None, metadata={}, page_count=0, chunks=[])

    fake_temp_file = FakeTemporaryFile()
    monkeypatch.setattr(
        "docforge.interfaces.pdf_routes.tempfile.NamedTemporaryFile",
        lambda *args, **kwargs: fake_temp_file,
    )
    monkeypatch.setattr(
        "docforge.interfaces.pdf_routes.parser_registry.get_parser",
        lambda content_type: FakeParser(fake_temp_file),
    )

    async def fake_read() -> bytes:
        return b"%PDF-1.4"

    file = SimpleNamespace(filename="sample.pdf", read=fake_read)
    result = asyncio.run(parse_pdf(file))

    assert result.metadata == {}
