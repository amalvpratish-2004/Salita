from fastapi import FastAPI
from app.api import knowledge, agent, voice

app = FastAPI(title="Salita Voice Agent API")

# Register routes
app.include_router(knowledge.router, prefix="/knowledge", tags=["Knowledge Base"])
app.include_router(agent.router, prefix="/agent", tags=["Voice Agent"])
app.include_router(voice.router, tags=["Realtime Call WebSocket"])

@app.get("/")
async def root():
    return {"status": "ok", "message": "Salita API is running!"}