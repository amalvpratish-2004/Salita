from fastapi import APIRouter
from pydantic import BaseModel
import sys
from pathlib import Path

# Temporarily add the rag directory to the path so we can import our retriever
sys.path.append(str(Path(__file__).parent.parent / "rag"))
from retriever import search_knowledge_base

router = APIRouter()

class SearchRequest(BaseModel):
    query: str
    top_k: int = 2

@router.post("/search")
async def search(request: SearchRequest):
    # Call the retriever function we just tested
    raw_results = search_knowledge_base(request.query, top_k=request.top_k)
    
    formatted_results = []
    # Check if we got any results back
    if raw_results.get('documents') and len(raw_results['documents']) > 0:
        for i in range(len(raw_results['documents'][0])):
            formatted_results.append({
                "text": raw_results['documents'][0][i],
                "metadata": raw_results['metadatas'][0][i],
                "distance": raw_results['distances'][0][i]
            })
            
    return {
        "query": request.query,
        "results": formatted_results
    }