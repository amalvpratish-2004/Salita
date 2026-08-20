import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import chromadb

# 1. Resolve paths cleanly relative to backend root
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
salita_root = backend_dir.parent
chroma_path = salita_root / "data" / "chroma"

sys.path.append(str(current_dir))

# Try importing custom embeddings if available; fallback to Chroma defaults
try:
    from embeddings import generate_embedding
    HAS_CUSTOM_EMBEDDINGS = True
except ImportError:
    HAS_CUSTOM_EMBEDDINGS = False


class KBRetriever:
    def __init__(self, collection_name: str = "salita_kb"):
        self.client = chromadb.PersistentClient(path=str(chroma_path))
        try:
            self.collection = self.client.get_collection(name=collection_name)
        except Exception:
            # Fallback to legacy collection if salita_kb isn't initialized yet
            try:
                self.collection = self.client.get_collection(name="business_knowledge")
            except Exception:
                self.collection = None

    def query(self, query_text: str, market_code: str = "EN", top_k: int = 3) -> str:
        """Query ChromaDB and return concatenated text chunks formatted for LLM context."""
        if not self.collection:
            return ""

        market = market_code.upper()
        where_filter = {"market_code": {"$in": [market, "EN"]}}

        try:
            if HAS_CUSTOM_EMBEDDINGS:
                embedding = generate_embedding(query_text)
                results = self.collection.query(
                    query_embeddings=[embedding],
                    n_results=top_k,
                    where=where_filter
                )
            else:
                results = self.collection.query(
                    query_texts=[query_text],
                    n_results=top_k,
                    where=where_filter
                )

            docs = results.get("documents", [[]])[0]
            return "\n\n".join(docs) if docs else ""
        except Exception as e:
            print(f"[KBRetriever Error] {e}")
            return ""


# Helper function for backward compatibility with your existing callers
def search_knowledge_base(query: str, market_code: str = "EN", top_k: int = 2) -> Dict[str, Any]:
    retriever = KBRetriever()
    if not retriever.collection:
        return {}

    where_filter = {"market_code": {"$in": [market_code.upper(), "EN"]}}

    if HAS_CUSTOM_EMBEDDINGS:
        query_embedding = generate_embedding(query)
        return retriever.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k,
            where=where_filter
        )
    else:
        return retriever.collection.query(
            query_texts=[query],
            n_results=top_k,
            where=where_filter
        )


if __name__ == "__main__":
    test_query = "What is the minimum monthly revenue required?"
    print(f"Testing Query: '{test_query}'\n")

    retriever = KBRetriever()
    context = retriever.query(test_query, market_code="PH")
    
    print("--- Retrieved Context Output ---")
    print(context if context else "No matching chunks found.")