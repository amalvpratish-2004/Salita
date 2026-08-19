import hashlib


def get_hash(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def remove_duplicates(documents):
    seen = set()
    unique_documents = []

    for document in documents:
        document_hash = get_hash(document)

        if document_hash not in seen:
            seen.add(document_hash)
            unique_documents.append(document)

    return unique_documents


if __name__ == "__main__":
    documents = [
        "Loan requires at least 2 years of business operation.",
        "Loan requires at least 2 years of business operation.",
        "Minimum monthly revenue is INR 50,000."
    ]

    unique = remove_duplicates(documents)

    print("Original documents:", len(documents))
    print("Unique documents:", len(unique))

    print("\nUnique documents:")
    for document in unique:
        print("-", document)