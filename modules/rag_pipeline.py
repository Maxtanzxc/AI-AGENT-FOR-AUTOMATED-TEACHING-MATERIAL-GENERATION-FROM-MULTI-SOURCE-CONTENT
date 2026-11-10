import chromadb
from chromadb.utils import embedding_functions
from modules.pdf_extractor import chunk_text

# Use a persistent ChromaDB client so data survives between runs
client = chromadb.PersistentClient(path="./data/chromadb")

# Use sentence-transformers for free local embeddings
embedding_fn = embedding_functions.SentenceTransformerEmbeddingFunction(
    model_name="all-MiniLM-L6-v2"
)


def get_or_create_collection(collection_name: str):
    """Get existing or create new ChromaDB collection."""
    try:
        return client.get_collection(
            name=collection_name,
            embedding_function=embedding_fn
        )
    except Exception:
        return client.create_collection(
            name=collection_name,
            embedding_function=embedding_fn
        )


def clear_collection(collection_name: str):
    """Clear a collection before loading new content."""
    try:
        client.delete_collection(collection_name)
    except Exception:
        pass
    return client.create_collection(
        name=collection_name,
        embedding_function=embedding_fn
    )


def add_to_collection(collection, text: str, source_label: str):
    """Chunk text and add to ChromaDB collection."""
    chunks = chunk_text(text)

    if not chunks:
        return 0

    ids = [f"{source_label}_chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": source_label} for _ in chunks]

    # ChromaDB has a batch limit so add in batches of 100
    batch_size = 100
    for i in range(0, len(chunks), batch_size):
        collection.add(
            documents=chunks[i:i + batch_size],
            ids=ids[i:i + batch_size],
            metadatas=metadatas[i:i + batch_size]
        )

    return len(chunks)


def retrieve_context(collection, topic: str, top_k: int = 5) -> str:
    """Retrieve most relevant chunks for a topic."""
    try:
        results = collection.query(
            query_texts=[topic],
            n_results=min(top_k, collection.count())
        )

        if not results["documents"][0]:
            return ""

        # Join retrieved chunks with source labels
        context_parts = []
        for doc, meta in zip(results["documents"][0], results["metadatas"][0]):
            context_parts.append(f"[Source: {meta['source']}]\n{doc}")

        return "\n\n".join(context_parts)

    except Exception as e:
        print(f"Retrieval error: {e}")
        return ""