import os
from pathlib import Path
import chromadb

# Import all the modules we built and tested
from loader import load_document
from cleaner import clean_text
from pii import mask_pii
from chunker import chunk_text
from metadata import add_metadata
from embeddings import generate_embeddings

# Setup paths dynamically
current_dir = Path(__file__).resolve().parent
salita_root = current_dir.parent.parent.parent
synthetic_dir = salita_root / "data" / "synthetic"
chroma_path = salita_root / "data" / "chroma"

# Connect to ChromaDB
client = chromadb.PersistentClient(path=str(chroma_path))
collection = client.get_or_create_collection(name="business_knowledge")

def process_directory():
    print(f"Scanning directory: {synthetic_dir}")
    
    # Loop through all files in the synthetic folder
    for filename in os.listdir(synthetic_dir):
        # Skip hidden files or unsupported types if needed
        if filename.startswith('.'):
            continue
            
        file_path = synthetic_dir / filename
        print(f"\n--- Processing: {filename} ---")
        
        # 1. Load, Clean, and Mask PII
        raw_text = load_document(file_path)
        if not raw_text:
            continue
            
        clean = clean_text(raw_text)
        safe_text = mask_pii(clean) # <--- PII masking is now applied!
        
        # 2. Chunk & Metadata
        chunks = chunk_text(safe_text)
        documents = add_metadata(chunks, source=filename)
        
        # 3. Embed
        embeddings = generate_embeddings(chunks)
        
        # 4. Prepare for Database
        ids = []
        texts = []
        metadatas = []
        
        for i, doc in enumerate(documents):
            # Create a unique ID using the filename to prevent overlaps
            ids.append(f"{filename}_chunk_{i}")
            texts.append(doc["text"])
            metadatas.append(doc["metadata"])
            
        # 5. Store (using upsert so we can run this script safely multiple times)
        collection.upsert(
            ids=ids,
            documents=texts,
            embeddings=embeddings,
            metadatas=metadatas
        )
        print(f"Successfully upserted {len(chunks)} chunks.")
        
    print(f"\nTotal chunks currently in Knowledge Base: {collection.count()}")

if __name__ == "__main__":
    process_directory()