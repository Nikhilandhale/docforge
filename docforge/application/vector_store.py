from __future__ import annotations

from typing import Protocol

import chromadb


class VectorStore(Protocol):
    def add_documents(
        self,
        documents: list[dict[str, object]],
        embeddings: list[list[float]],
    ) -> None: ...

    def search(self, query: str, top_k: int = 5) -> list[dict[str, object]]: ...

    def get_chunk_count(self) -> int: ...


class ChromaVectorStore:
    def __init__(self, collection_name: str, persist_directory: str) -> None:
        self.client = chromadb.PersistentClient(path=persist_directory)
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(
        self,
        documents: list[dict[str, object]],
        embeddings: list[list[float]],
    ) -> None:
        if not documents:
            return

        self.collection.upsert(
            ids=[f"{document['document_id']}-{document['chunk_index']}" for document in documents],
            documents=[str(document["text"]) for document in documents],
            embeddings=embeddings,
            metadatas=[
                {key: value for key, value in document.items() if key != "text"}
                for document in documents
            ],
        )

    def search(
        self,
        query: str,
        top_k: int = 5,
        metadata_filter: dict[str, object] | None = None,
    ) -> list[dict[str, object]]:
        if not query.strip():
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=metadata_filter,
        )
        documents = results.get("documents", [[]])[0]
        metadatas = results.get("metadatas", [[]])[0]
        output: list[dict[str, object]] = []

        for index, document in enumerate(documents):
            metadata = metadatas[index] if index < len(metadatas) else {}
            output.append({"text": document, **metadata})

        return output

    def get_chunk_count(self) -> int:
        return self.collection.count()
