import os

import chromadb
from chromadb.config import Settings as ChromaSettings

from app.config import settings

chroma_client = chromadb.Client(ChromaSettings(
    chroma_db_impl="duckdb+parquet",
    persist_directory=settings.chroma_persist_dir,
    anonymized_telemetry=False,
))

COLLECTION_NAME = "knowledge_base"


def get_or_create_collection():
    return chroma_client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def add_document(doc_id: str, content: str, metadata: dict | None = None):
    collection = get_or_create_collection()

    chunks = _split_text(content, chunk_size=500, overlap=50)

    ids = [f"{doc_id}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [metadata or {} for _ in chunks]

    collection.add(
        documents=chunks,
        ids=ids,
        metadatas=metadatas,
    )

    return len(chunks)


def query_knowledge_base(query: str, n_results: int = 3) -> str:
    collection = get_or_create_collection()

    if collection.count() == 0:
        return ""

    results = collection.query(
        query_texts=[query],
        n_results=n_results,
    )

    if not results["documents"] or not results["documents"][0]:
        return ""

    context_parts = []
    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
        source = metadata.get("source", "Onbekend")
        context_parts.append(f"[Bron: {source}]\n{doc}")

    return "\n\n---\n\n".join(context_parts)


def ingest_file(file_path: str, doc_type: str, source: str) -> int:
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()

    doc_id = os.path.basename(file_path).replace(".", "_")
    metadata = {"source": source, "doc_type": doc_type, "file": file_path}

    return add_document(doc_id, content, metadata)


def _split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    words = text.split()
    chunks = []
    start = 0

    while start < len(words):
        end = start + chunk_size
        chunk = " ".join(words[start:end])
        chunks.append(chunk)
        start = end - overlap

    return chunks if chunks else [text]
