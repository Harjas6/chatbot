from pathlib import Path

from rag.pdf import model
from rag.store_vectors import collection

# chroma uses L2 as default. 1 == to 0.5 in cosine similarity
THRESHOLD = 1.0


def display_name(stored_name: str) -> str:
    path = Path(stored_name)
    base = path.stem.rsplit("_", 1)[0]  # drop everything after the last underscore
    return base + path.suffix


def retrieve_chunks(query: str, n_results: int = 5):
    query_embedding = model.encode(
        query,
        normalize_embeddings=True,
    ).tolist()

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
        include=["documents", "distances", "metadatas"],
    )

    chunks = results["documents"][0]  # type: ignore
    distances = results["distances"][0]  # type: ignore
    metadatas = results["metadatas"][0]  # type: ignore

    return [
        (chunk, display_name(str(metadata["filename"])))
        for chunk, distance, metadata in zip(chunks, distances, metadatas)
        if distance <= THRESHOLD
    ]
