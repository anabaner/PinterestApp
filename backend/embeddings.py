import chromadb
from sentence_transformers import SentenceTransformer

# Load the embedding model once at startup (downloads ~90MB first time)
embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

# ChromaDB stores everything in a local folder called chroma_store/
chroma_client = chromadb.PersistentClient(path="./chroma_store")
#collection = chroma_client.get_or_create_collection(name="pins")

# New (uses cosine distance — correct for sentence embeddings)
collection = chroma_client.get_or_create_collection(
    name="pins_cosine",
    metadata={"hnsw:space": "cosine"}
)


def pin_to_text(title: str, description: str, tags: str) -> str:
    """Combine pin fields into one string for embedding."""
    return f"{title}. {description}. {tags.replace(',', ' ')}"


def add_pin_embedding(pin_id: int, title: str, description: str, tags: str):
    """Generate and store an embedding for a pin."""
    text = pin_to_text(title, description, tags)
    embedding = embedding_model.encode(text).tolist()

    collection.upsert(
        ids=[str(pin_id)],
        embeddings=[embedding],
        metadatas=[{"title": title, "tags": tags}]
    )


def get_similar_pin_ids(pin_id: int, n: int = 3,threshold: float = 0.75) -> list[int]:
    """Find the n most similar pins to a given pin."""
    results = collection.get(
        ids=[str(pin_id)],
        include=["embeddings"]
    )

    if results["embeddings"] is None or len(results["embeddings"]) == 0:
        return []

    query_embedding = results["embeddings"][0]

    similar = collection.query(
        query_embeddings=[query_embedding],
        n_results=n + 1,
        include=["distances"]
    )
    ids = similar["ids"][0]
    distances = similar["distances"][0]

    # Zip ids and distances together, filter by threshold and exclude self
    similar_ids = [
        int(id_)
        for id_, dist in zip(ids, distances)
        if int(id_) != pin_id and dist < threshold
    ]

    return similar_ids[:n]


def delete_pin_embedding(pin_id: int):
    """Remove a pin's embedding when the pin is deleted."""
    try:
        collection.delete(ids=[str(pin_id)])
    except Exception:
        pass  # ignore if it doesn't exist

def debug_distances(pin_id: int):
    """Print actual distances so you can pick the right threshold."""
    results = collection.get(
        ids=[str(pin_id)],
        include=["embeddings"]
    )

    if results["embeddings"] is None or len(results["embeddings"]) == 0:
        print("Pin not found in ChromaDB")
        return

    query_embedding = results["embeddings"][0]

    similar = collection.query(
        query_embeddings=[query_embedding],
        n_results=10,
        include=["distances", "metadatas"]
    )

    print("\n--- Similarity distances for pin", pin_id, "---")
    for id_, dist, meta in zip(
        similar["ids"][0],
        similar["distances"][0],
        similar["metadatas"][0]
    ):
        print(f"  Pin {id_:>3} | distance: {dist:.4f} | title: {meta['title']}")
    print("---\n")