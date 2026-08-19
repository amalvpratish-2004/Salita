import chromadb


# Create a persistent ChromaDB database
client = chromadb.PersistentClient(
    path="../../../data/chroma"
)

# Create or load our collection
collection = client.get_or_create_collection(
    name="business_knowledge"
)


def add_documents(documents, embeddings):
    ids = []
    texts = []
    metadatas = []

    for i, document in enumerate(documents):
        ids.append(f"chunk_{i}")
        texts.append(document["text"])
        metadatas.append(document["metadata"])

    collection.add(
        ids=ids,
        documents=texts,
        embeddings=embeddings,
        metadatas=metadatas
    )


if __name__ == "__main__":
    from loader import load_text_file
    from cleaner import clean_text
    from chunker import chunk_text
    from metadata import add_metadata
    from embeddings import generate_embeddings

    file_path = "../../../data/synthetic/loan_eligibility.txt"

    raw_text = load_text_file(file_path)
    clean = clean_text(raw_text)

    chunks = chunk_text(clean)

    documents = add_metadata(
        chunks,
        source="loan_eligibility.txt"
    )

    embeddings = generate_embeddings(chunks)

    add_documents(documents, embeddings)

    print("Documents added to ChromaDB!")
    print("Number of documents:", collection.count())