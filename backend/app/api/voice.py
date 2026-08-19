from fastapi import APIRouter, WebSocket, WebSocketDisconnect
import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "ai"))
sys.path.append(str(backend_dir / "app" / "agent"))
sys.path.append(str(backend_dir / "app" / "realtime"))

from asr import transcribe_audio_bytes
from orchestrator import LoanAgentOrchestrator
from tts import generate_audio_stream
from signals import NudgeEngine

router = APIRouter()
nudge_engine = NudgeEngine()

@router.websocket("/ws/call")
async def voice_call_endpoint(websocket: WebSocket):
    await websocket.accept()
    # Instantiate fresh session state for each new call
    orchestrator = LoanAgentOrchestrator()
    print("[WebSocket] Client connected to live call.")

    try:
        while True:
            audio_data = await websocket.receive_bytes()

            user_text = transcribe_audio_bytes(audio_data)
            if not user_text:
                continue

            await websocket.send_json({"type": "transcript", "speaker": "User", "text": user_text})

            nudge = nudge_engine.analyze_transcript_chunk(f"Customer: {user_text}")
            if nudge:
                await websocket.send_json({
                    "type": "nudge",
                    "signal": nudge.signal,
                    "text": nudge.nudge_text,
                    "confidence": nudge.confidence,
                    "priority": nudge.priority
                })

            agent_text = orchestrator.process_message(user_text)
            status, _ = orchestrator.state.evaluate_eligibility()
            
            await websocket.send_json({
                "type": "transcript",
                "speaker": "Salita",
                "text": agent_text,
                "qualification_status": status,
                "missing_field": orchestrator.state.get_missing_field()
            })

            audio_path = "temp_agent_response.mp3"
            await generate_audio_stream(agent_text, voice="en-US-AriaNeural", output_path=audio_path)
            
            with open(audio_path, "rb") as f:
                await websocket.send_bytes(f.read())

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")