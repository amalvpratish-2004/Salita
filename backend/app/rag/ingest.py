import os
import re
import csv
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "rag"))

import chromadb
from chromadb.utils import embedding_functions

DATA_DIR = backend_dir.parent / "data" / "synthetic"
CHROMA_DB_DIR = backend_dir / "chroma_db"

def extract_market_code(file_path: Path, content: str) -> str:
    """Extract market_code from YAML metadata or filename."""
    if "market_code: PH" in content or "_philippines_" in file_path.name:
        return "PH"
    if "market_code: ID" in content or "_indonesia_" in file_path.name:
        return "ID"
    return "EN"

def load_and_parse_files(data_dir: Path):
    documents = []
    metadatas = []
    ids = []
    
    doc_id = 0
    for file_path in data_dir.glob("*"):
        if file_path.suffix not in [".txt", ".csv"]:
            continue
            
        market_code = "EN"
        raw_text = ""

        if file_path.suffix == ".txt":
            with open(file_path, "r", encoding="utf-8") as f:
                raw_text = f.read()
            market_code = extract_market_code(file_path, raw_text)

        elif file_path.suffix == ".csv":
            rows = []
            with open(file_path, "r", encoding="utf-8") as f:
                reader = csv.reader(f)
                for row in reader:
                    rows.append(" | ".join(row))
            raw_text = f"CSV File ({file_path.name}):\n" + "\n".join(rows)

        # Basic paragraph chunking to avoid splitting mid-sentence
        chunks = [c.strip() for c in re.split(r'\n\s*\n', raw_text) if len(c.strip()) > 20]
        
        for idx, chunk in enumerate(chunks):
            doc_id += 1
            documents.append(chunk)
            metadatas.append({
                "source": file_path.name,
                "market_code": market_code,
                "chunk_index": idx
            })
            ids.append(f"doc_{doc_id}")

    return documents, metadatas, ids

def ingest_knowledge_base():
    print(f"Reading files from {DATA_DIR}...")
    documents, metadatas, ids = load_and_parse_files(DATA_DIR)
    
    if not documents:
        print("❌ No documents found to ingest!")
        return

    print(f"Loaded {len(documents)} text chunks from {DATA_DIR.name}.")

    client = chromadb.PersistentClient(path=str(CHROMA_DB_DIR))
    
    # Reset collection to ensure fresh indexing
    try:
        client.delete_collection(name="salita_kb")
    except Exception:
        pass

    collection = client.create_collection(
        name="salita_kb",
        metadata={"hnsw:space": "cosine"}
    )

    collection.add(
        documents=documents,
        metadatas=metadatas,
        ids=ids
    )

    print(f"✅ Successfully ingested {len(documents)} chunks into ChromaDB at {CHROMA_DB_DIR}.")

if __name__ == "__main__":
    ingest_knowledge_base()