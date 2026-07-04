import importlib
import os
from pathlib import Path

import fitz
from fastapi.testclient import TestClient


def build_client(tmp_path: Path):
    db_path = tmp_path / "test-docforge.db"
    storage_dir = tmp_path / "storage"
    os.environ["DOCFORGE_DATABASE_URL"] = f"sqlite:///{db_path}"
    os.environ["DOCFORGE_STORAGE_DIR"] = str(storage_dir)

    import docforge.config as config
    import docforge.infrastructure.database as database
    import docforge.main as main

    importlib.reload(config)
    importlib.reload(database)
    importlib.reload(main)

    database.create_db_and_tables()
    return TestClient(main.app)


def test_upload_rejects_non_pdf_files(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    response = client.post(
        "/documents/upload",
        files={"file": ("notes.txt", b"not a pdf", "text/plain")},
    )

    assert response.status_code == 415
    assert "Only PDF files are supported" in response.json()["detail"]


def test_upload_accepts_pdf_and_persists_metadata(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    pdf_bytes = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog >>\nendobj\ntrailer\n<< /Root 1 0 R >>\n%%EOF"

    response = client.post(
        "/documents/upload",
        files={"file": ("sample.pdf", pdf_bytes, "application/pdf")},
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["original_filename"] == "sample.pdf"
    assert payload["content_type"] == "application/pdf"
    assert payload["status"] == "uploaded"
    assert payload["file_size_bytes"] == len(pdf_bytes)
    assert payload["storage_path"].endswith("sample.pdf")


def test_upload_pipeline_indexes_document_for_chat(tmp_path: Path) -> None:
    client = build_client(tmp_path)

    pdf_path = tmp_path / "indexed.pdf"
    document = fitz.open()
    page = document.new_page()
    page.insert_text((72, 72), "DocForge indexing test content")
    document.save(pdf_path)
    document.close()

    upload_response = client.post(
        "/documents/upload",
        files={"file": ("indexed.pdf", pdf_path.read_bytes(), "application/pdf")},
    )

    assert upload_response.status_code == 201
    document_id = upload_response.json()["id"]

    chat_response = client.post(
        "/chat",
        json={"document_id": str(document_id), "question": "What is this document about?"},
    )

    assert chat_response.status_code == 200
    assert chat_response.json()["source_page_numbers"] == [1]
    assert chat_response.json()["retrieved_chunk_metadata"]
