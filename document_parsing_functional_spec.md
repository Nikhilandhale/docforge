# Functional Specification: DocForge PDF Ingestion and Retrieval

## 1. Purpose

DocForge implements a lightweight document ingestion pipeline for PDF documents. The current MVP accepts uploaded files, stores them locally, extracts text, chunks the content, generates embeddings, indexes the chunks, and supports retrieval-based question answering.

## 2. Scope

In scope:
- Uploading a single PDF document through the API
- Persisting document metadata in SQLite
- Storing uploaded files in the configured local storage directory
- Parsing PDF text with PyMuPDF
- Producing normalized document chunks for indexing
- Generating embeddings and indexing chunks in ChromaDB
- Retrieving relevant chunks and returning grounded answers with source page numbers

Out of scope for the current MVP:
- Multi-format document ingestion beyond PDF
- Asynchronous background processing
- Advanced authentication and enterprise deployment features

## 3. Core Workflow

1. A user uploads a PDF document to the upload endpoint.
2. The application validates the file and saves it to local storage.
3. The PDF is parsed to extract text and metadata.
4. The parsed text is chunked into smaller units.
5. Embeddings are generated for each chunk.
6. Chunks are indexed in ChromaDB for semantic retrieval.
7. A user can ask a question through the chat endpoint and receive a grounded response.

## 4. Functional Requirements

### 4.1 Upload Flow

The system must:
- Accept PDF files only
- Reject empty or invalid uploads with clear error responses
- Persist document metadata in SQLite
- Store the uploaded file in a local directory

### 4.2 Parsing Flow

The system must:
- Parse uploaded PDFs using PyMuPDF
- Extract document text and page-level metadata
- Produce normalized chunk objects for downstream indexing

### 4.3 Indexing and Retrieval

The system must:
- Generate embeddings for each chunk
- Index chunks in ChromaDB using document identifiers and page metadata
- Retrieve relevant chunks for a submitted question

### 4.4 Chat Endpoint

The chat endpoint must:
- Accept a document identifier and a question
- Return a grounded answer based on retrieved chunks
- Include source page numbers and retrieved chunk metadata

## 5. Current API Surface

The MVP currently exposes:
- POST /documents/upload
- GET /documents
- GET /documents/{document_id}
- POST /parse/pdf
- POST /chat
- GET /health
