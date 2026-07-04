from __future__ import annotations

import logging
import tempfile
from pathlib import Path

from fastapi import APIRouter, HTTPException, UploadFile, status

from docforge.application.parsers import PDFParser, ParserRegistry
from docforge.domain.parsing_models import ParsedDocument

logger = logging.getLogger("docforge")

router = APIRouter(prefix="/parse", tags=["parsing"])
parser_registry = ParserRegistry()
parser_registry.register("application/pdf", PDFParser())


@router.post("/pdf", response_model=ParsedDocument, status_code=status.HTTP_200_OK)
async def parse_pdf(file: UploadFile) -> ParsedDocument:
    """Parse an uploaded PDF file into a normalized internal representation."""
    if file.filename is None or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=415, detail="Only PDF files are supported")

    parser = parser_registry.get_parser("application/pdf")
    if parser is None:
        raise HTTPException(status_code=500, detail="PDF parser is not available")

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as temp_file:
        temp_path = Path(temp_file.name)
        try:
            content = await file.read()
            temp_path.write_bytes(content)
            temp_file.flush()
            temp_file.close()
            parsed_document = parser.parse(temp_path)
            return parsed_document
        except OSError as exc:
            logger.exception("Failed to write temporary PDF for parsing")
            raise HTTPException(status_code=400, detail="Could not process uploaded PDF") from exc
        finally:
            try:
                if temp_path.exists():
                    temp_path.unlink(missing_ok=True)
            except PermissionError:
                logger.warning("Temporary PDF file was still locked during cleanup: %s", temp_path)
