from pathlib import Path


def load_text_file(file_path):
    path = Path(file_path)

    with open(path, "r", encoding="utf-8") as file:
        text = file.read()

    return text


if __name__ == "__main__":
    file_path = "../../../data/synthetic/loan_eligibility.txt"

    text = load_text_file(file_path)

    print("Document loaded successfully!")
    print("Characters:", len(text))
    print()
    print(text)