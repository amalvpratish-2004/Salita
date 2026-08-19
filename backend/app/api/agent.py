from fastapi import APIRouter
from pydantic import BaseModel
import sys
from pathlib import Path

# Path setup to import orchestrator
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "agent"))

from orchestrator import LoanAgentOrchestrator

router = APIRouter()

# Instantiate a global session agent (for multi-user support, this can be session-keyed)
orchestrator = LoanAgentOrchestrator()

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    missing_field: str | None
    qualification_status: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(request: ChatRequest):
    agent_response = orchestrator.process_message(request.message)
    status, _ = orchestrator.state.evaluate_eligibility()
    
    return ChatResponse(
        response=agent_response,
        missing_field=orchestrator.state.get_missing_field(),
        qualification_status=status
    )