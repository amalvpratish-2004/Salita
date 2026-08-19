from pathlib import Path
import pypdf
import pandas as pd

def load_text_file(file_path):
    path = Path(file_path)
    with open(path, "r", encoding="utf-8") as file:
        return file.read()

def load_pdf_file(file_path):
    text = ""
    with open(file_path, "rb") as file:
        reader = pypdf.PdfReader(file)
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
    return text

def load_csv_file(file_path):
    # Pandas is great for reading tabular data and converting it to readable text
    df = pd.read_csv(file_path)
    return df.to_string()

def load_document(file_path):
    """Dynamically chooses the right loader based on file extension."""
    path = Path(file_path)
    ext = path.suffix.lower()
    
    if ext == ".txt":
        return load_text_file(path)
    elif ext == ".pdf":
        return load_pdf_file(path)
    elif ext == ".csv":
        return load_csv_file(path)
    else:
        print(f"Warning: Unsupported file type {ext}")
        return ""

if __name__ == "__main__":
    # Test our router on the existing txt file
    file_path = "../../../data/synthetic/loan_eligibility.txt"
    text = load_document(file_path)
    print("Generic loader works! Characters:", len(text))