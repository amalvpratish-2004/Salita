def add_metadata(chunks, source, document_type="synthetic_policy"):
    documents = []

    for i, chunk in enumerate(chunks):
        document = {
            "text": chunk,
            "metadata": {
                "source": source,
                "chunk_id": i,
                "document_type": document_type
            }
        }

        documents.append(document)

    return documents


if __name__ == "__main__":
    from loader import load_text_file
    from cleaner import clean_text
    from chunker import chunk_text

    file_path = "../../../data/synthetic/loan_eligibility.txt"

    raw_text = load_text_file(file_path)
    clean = clean_text(raw_text)
    chunks = chunk_text(clean)

    documents = add_metadata(
        chunks,
        source="loan_eligibility.txt"
    )

    for document in documents:
        print(document)
        print()