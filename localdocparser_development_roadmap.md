# DocForge Development Roadmap

DocForge is currently in its MVP phase. The roadmap below reflects the work that is already implemented and the next improvements planned for release readiness.

## Current status

Implemented in the current release:
- PDF upload and local storage
- SQLite-backed document metadata persistence
- PDF parsing with PyMuPDF
- Text chunking and normalization
- Embedding generation with SentenceTransformers
- ChromaDB-based indexing and retrieval
- A chat endpoint with grounded answers and source page references
- FastAPI documentation and Docker-based local setup

## Short-term priorities

- Improve parsing robustness for edge cases and larger PDFs
- Refine chunking and retrieval quality
- Expand automated test coverage around parsing and retrieval behavior
- Improve operational guidance and error handling

## Medium-term priorities

- Add support for additional document formats beyond PDF
- Improve retrieval relevance and answer grounding
- Introduce asynchronous processing for larger workloads
- Strengthen observability and deployment readiness

## Release philosophy

DocForge will continue to evolve in small, testable increments while keeping the current MVP stable and easy to use.
| Upload and Job Management | Medium |
| Storage and Artifact Persistence | Medium |
| Parser Registry and Initial Parser Plugin | High |
| Metadata Extraction and Schema Inference | High |
| Validation Pipeline | Medium |
| Result Generation and Preview API | Medium |
| Background Processing and Async Workers | High |
| Observability, Security, and Operational Readiness | Medium |
| Multi-Parser Expansion and Extensibility Hardening | Medium |

---

## Suggested Release Strategy

- Release 1: Milestones 1–4
- Release 2: Milestones 5–8
- Release 3: Milestones 9–11

This balances early user value with a structured path toward a robust and extensible platform.
