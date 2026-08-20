import sys
import uuid
from typing import Dict, Optional
from pathlib import Path
from fastapi import APIRouter, Header
from pydantic import BaseModel

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "agent"))

from orchestrator import LoanAgentOrchestrator

router = APIRouter()

# Session registry mapping session_id -> LoanAgentOrchestrator instance
session_registry: Dict[str, LoanAgentOrchestrator] = {}

class ChatRequest(BaseModel):
    message: str

class ChatResponse(BaseModel):
    response: str
    missing_field: Optional[str]
    qualification_status: str
    session_id: str

@router.post("/chat", response_model=ChatResponse)
async def chat_with_agent(
    request: ChatRequest, 
    x_session_id: Optional[str] = Header(None)
):
    # Use existing session ID from headers or generate a new unique session key
    session_id = x_session_id or str(uuid.uuid4())
    
    if session_id not in session_registry:
        session_registry[session_id] = LoanAgentOrchestrator()
        
    orchestrator = session_registry[session_id]
    agent_response = orchestrator.process_message(request.message)
    status, _ = orchestrator.state.evaluate_eligibility()
    
    return ChatResponse(
        response=agent_response,
        missing_field=orchestrator.state.get_missing_field(),
        qualification_status=status,
        session_id=session_id
    )