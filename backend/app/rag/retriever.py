from embeddings import generate_embedding
from vector_store import collection


def search_knowledge(query, top_k=3):
    query_embedding = generate_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )

    documents = []

    for i, text in enumerate(results["documents"][0]):
        metadata = results["metadatas"][0][i]

        documents.append({
            "text": text,
            "source": metadata["source"],
            "chunk_id": metadata["chunk_id"],
            "document_type": metadata["document_type"]
        })

    return documents


if __name__ == "__main__":
    query = "What is the minimum monthly revenue?"

    results = search_knowledge(query)

    print("Query:", query)
    print()

    for i, result in enumerate(results):
        print(f"--- Result {i + 1} ---")
        print("Text:", result["text"])
        print("Source:", result["source"])
        print("Chunk ID:", result["chunk_id"])
        print("Document type:", result["document_type"])
        print()