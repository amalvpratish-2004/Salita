from sentence_transformers import SentenceTransformer


model = SentenceTransformer("all-MiniLM-L6-v2")


def generate_embedding(text):
    embedding = model.encode(text)
    return embedding.tolist()


def generate_embeddings(chunks):
    embeddings = []

    for chunk in chunks:
        embedding = generate_embedding(chunk)
        embeddings.append(embedding)

    return embeddings


if __name__ == "__main__":
    from loader import load_text_file
    from cleaner import clean_text
    from chunker import chunk_text

    file_path = "../../../data/synthetic/loan_eligibility.txt"

    raw_text = load_text_file(file_path)
    clean = clean_text(raw_text)
    chunks = chunk_text(clean)

    embeddings = generate_embeddings(chunks)

    print("Number of chunks:", len(chunks))
    print("Number of embeddings:", len(embeddings))

    for i, embedding in enumerate(embeddings):
        print(
            f"Chunk {i}: "
            f"{len(embedding)} dimensions"
        )