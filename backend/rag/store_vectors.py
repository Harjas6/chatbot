from pathlib import Path

import chromadb

BACKEND_DIR = Path(__file__).resolve().parent.parent
CHROMA_DIR = BACKEND_DIR / "chroma_db"
client = chromadb.PersistentClient(path=CHROMA_DIR)
collection = client.get_or_create_collection(name="pdf_documents")


def store_vectors(
    chunks: list[str],
    embeddings: list[list[float]],
    filename: str,
) -> None:
    collection.add(
        ids=[f"{filename}_{i}" for i in range(len(chunks))],
        documents=chunks,
        embeddings=embeddings,  # type: ignore
        metadatas=[{"filename": filename} for _ in chunks],
    )
