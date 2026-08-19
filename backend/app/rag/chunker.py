def chunk_text(text, chunk_size=400, overlap=50):
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunk = text[start:end]
        chunks.append(chunk)

        start = end - overlap

    return chunks


if __name__ == "__main__":
    from loader import load_text_file
    from cleaner import clean_text

    file_path = "../../../data/synthetic/loan_eligibility.txt"

    raw_text = load_text_file(file_path)
    clean = clean_text(raw_text)

    chunks = chunk_text(clean)

    print("Number of chunks:", len(chunks))

    for i, chunk in enumerate(chunks):
        print("\n--- Chunk", i, "---")
        print(chunk)