import io
import sys
import edge_tts
from pathlib import Path
from fastapi import APIRouter, WebSocket, WebSocketDisconnect

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "ai"))
sys.path.append(str(backend_dir / "app" / "agent"))
sys.path.append(str(backend_dir / "app" / "realtime"))

from asr import transcribe_audio_bytes
from orchestrator import LoanAgentOrchestrator
from signals import NudgeEngine

router = APIRouter()
nudge_engine = NudgeEngine()

@router.websocket("/ws/call")
async def voice_call_endpoint(websocket: WebSocket):
    await websocket.accept()
    orchestrator = LoanAgentOrchestrator()
    print("[WebSocket] Client connected to live call.")

    try:
        while True:
            audio_data = await websocket.receive_bytes()

            # 1. Speech to Text
            user_text = transcribe_audio_bytes(audio_data)
            if not user_text:
                continue

            await websocket.send_json({"type": "transcript", "speaker": "User", "text": user_text})

            # 2. Real-time Nudge Check
            nudge = nudge_engine.analyze_transcript_chunk(f"Customer: {user_text}")
            if nudge:
                await websocket.send_json({
                    "type": "nudge",
                    "signal": nudge.signal,
                    "text": nudge.nudge_text,
                    "confidence": nudge.confidence,
                    "priority": nudge.priority
                })

            # 3. Agent Processing
            agent_text = orchestrator.process_message(user_text)
            status, _ = orchestrator.state.evaluate_eligibility()

            await websocket.send_json({
                "type": "transcript",
                "speaker": "Salita",
                "text": agent_text,
                "qualification_status": status,
                "missing_field": orchestrator.state.get_missing_field()
            })

            # 4. In-Memory TTS Audio Generation (Zero Disk Latency)
            communicate = edge_tts.Communicate(agent_text, "en-US-AriaNeural")
            buffer = io.BytesIO()
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    buffer.write(chunk["data"])

            await websocket.send_bytes(buffer.getvalue())

    except WebSocketDisconnect:
        print("[WebSocket] Client disconnected.")