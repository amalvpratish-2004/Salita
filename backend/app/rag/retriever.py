import chromadb
import sys
from pathlib import Path

# 1. Ensure we can always import embeddings, whether run directly or via FastAPI
current_dir = Path(__file__).resolve().parent
sys.path.append(str(current_dir))
from embeddings import generate_embedding

# 2. Dynamically calculate the absolute path to Salita/data/chroma
# current_dir is backend/app/rag, so we go up 3 levels to get to Salita/
salita_root = current_dir.parent.parent.parent
chroma_path = salita_root / "data" / "chroma"

# 3. Connect using the absolute path
client = chromadb.PersistentClient(path=str(chroma_path))

# Get our existing collection
collection = client.get_collection(name="business_knowledge")

def search_knowledge_base(query, top_k=2):
    # 1. Embed the user's query using the exact same model
    query_embedding = generate_embedding(query)
    
    # 2. Search the ChromaDB collection
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k
    )
    
    return results

if __name__ == "__main__":
    # Test a semantic question that should map to our synthetic document
    test_query = "What is the minimum monthly revenue required?"
    print(f"Question: '{test_query}'\n")
    
    results = search_knowledge_base(test_query, top_k=2)
    
    # Display the results with explicit citations/metadata
    # ChromaDB returns lists of lists, so we access index 0
    for i in range(len(results['documents'][0])):
        text = results['documents'][0][i]
        metadata = results['metadatas'][0][i]
        distance = results['distances'][0][i] 
        
        print(f"--- Result {i+1} ---")
        print(f"Citation: {metadata['source']} (Chunk {metadata['chunk_id']})")
        print(f"Distance: {distance:.4f}") # Lower distance = closer match
        print(f"Text:\n{text}\n")