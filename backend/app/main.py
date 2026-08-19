from fastapi import FastAPI
from app.api import knowledge

app = FastAPI(title="Salita Voice Agent API")

# Register our knowledge base endpoints
app.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "Salita API is running!"}