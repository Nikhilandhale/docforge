from pathlib import Path

import fitz

from docforge.application.indexing import IndexingService
from docforge.domain.parsing_models import ParsedDocument
from docforge.application.parsers import PDFParser
from docforge.application.embeddings import SentenceTransformerEmbeddingService
from docforge.application.vector_store import ChromaVectorStore


def test_indexing_service_indexes_parsed_document(tmp_path: Path) -> None:
    pdf_path = tmp_path / "sample.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "Alpha beta gamma")
    document.save(pdf_path)
    document.close()

    parser = PDFParser(chunk_size=20, chunk_overlap=0)
    parsed = parser.parse(pdf_path)

    embedding_service = SentenceTransformerEmbeddingService(model_name="sentence-transformers/all-MiniLM-L6-v2")
    vector_store = ChromaVectorStore(collection_name="test-docforge", persist_directory=str(tmp_path / "chroma"))
    indexing_service = IndexingService(embedding_service=embedding_service, vector_store=vector_store)

    result = indexing_service.index_document(parsed, document_id="doc-123")

    assert result is True
    assert vector_store.get_chunk_count() >= 1


def test_vector_store_returns_empty_results_for_unknown_query(tmp_path: Path) -> None:
    vector_store = ChromaVectorStore(collection_name="test-docforge-empty", persist_directory=str(tmp_path / "chroma-empty"))

    results = vector_store.search("unknown query", top_k=3)

    assert results == []
