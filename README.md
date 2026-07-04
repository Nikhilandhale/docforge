# DocForge

[![Python 3.12+](https://img.shields.io/badge/Python-3.12%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-pytest-4c1?logo=pytest&logoColor=white)](https://pytest.org/)

DocForge is an open-source document intelligence platform for ingesting PDF documents, extracting their content, indexing it for semantic retrieval, and answering questions with grounded responses.

## What DocForge does

DocForge provides a modular backend for document ingestion and retrieval. The current implementation is an MVP focused on PDF workflows with:

- PDF upload and local file storage
- SQLite-backed document metadata persistence
- PDF parsing with PyMuPDF
- Text chunking and normalization
- Embedding generation with SentenceTransformers
- Vector indexing and retrieval with ChromaDB
- A chat endpoint that returns grounded answers with source page references
- FastAPI-generated OpenAPI documentation
- Docker-based local development support

## Technology stack

DocForge is built with:

- Python 3.12+
- FastAPI
- Pydantic v2 and pydantic-settings
- SQLModel
- Python multipart support for uploads
- PyMuPDF
- SentenceTransformers
- ChromaDB
- pytest and Ruff

## Project structure

```text
docforge/
  application/
  domain/
  infrastructure/
  interfaces/
  main.py
  config.py
tests/
```

## Installation

Requirements:
- Python 3.12+
- Poetry

Install dependencies:

```bash
poetry install
```

## Configuration

The application reads the following environment variables with the `DOCFORGE_` prefix:

```env
DOCFORGE_APP_ENV=development
DOCFORGE_APP_DEBUG=true
DOCFORGE_APP_HOST=0.0.0.0
DOCFORGE_APP_PORT=8000
DOCFORGE_DATABASE_URL=sqlite:///./docforge.db
DOCFORGE_STORAGE_DIR=./storage
```

A template is available in [.env.example](.env.example).

## Running locally

Start the API server:

```bash
poetry run uvicorn docforge.main:app --reload
```

Then open:
- http://127.0.0.1:8000/docs for Swagger UI
- http://127.0.0.1:8000/redoc for ReDoc

## Docker usage

Build and run the service with Docker Compose:

```bash
docker compose up --build
```

The API is exposed on port 8000.

## API workflow

1. Upload a PDF to `/documents/upload`
2. Retrieve its metadata from `/documents/{document_id}`
3. Send a question to `/chat` along with the document ID
4. Receive an answer and the source pages used for retrieval

## Testing

Run the full test suite:

```bash
poetry run pytest
```

## Current status

DocForge is currently an MVP focused on PDF-based ingestion and retrieval. It supports the core upload, parsing, indexing, and chat workflow end to end.

## Contributing

Contributions are welcome. Please see [CONTRIBUTING.md](CONTRIBUTING.md) for setup, testing, and pull request guidance.

## License

DocForge is distributed under the MIT License. See [LICENSE](LICENSE) for details.
