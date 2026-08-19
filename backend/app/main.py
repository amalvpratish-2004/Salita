from fastapi import FastAPI
from app.api import knowledge, agent

app = FastAPI(title="Salita Voice Agent API")

# Register routes
app.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
app.include_router(agent.router, prefix="/agent", tags=["Voice Agent"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "Salita API is running!"}