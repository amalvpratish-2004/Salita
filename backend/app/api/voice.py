import sys
import asyncio
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
from multilingual_agent import LocalizedVoiceAgent
from signals import NudgeEngine
from market_config import get_market_config  # Imported your exact function

router = APIRouter()
nudge_engine = NudgeEngine()

@router.websocket("/ws/call")
async def voice_call_endpoint(websocket: WebSocket, market: str = "EN"):
    await websocket.accept()
    
    market_code = market.upper()
    
    # 1. Market Routing & Voice/ASR Selection
    if market_code in ["PH", "ID"]:
        market_cfg = get_market_config(market_code)
        tts_voice = market_cfg.tts_voice_female
        # faster-whisper uses "tl" for Tagalog/Taglish and "id" for Indonesia
        asr_lang = "tl" if market_code == "PH" else "id"
        orchestrator = LocalizedVoiceAgent(market_code=market_code)
    else:
        # Default to English
        tts_voice = "en-US-AriaNeural"
        asr_lang = "en"
        orchestrator = LoanAgentOrchestrator()

    print(f"[WebSocket] Client connected. Market: {market_code}")

    try:
        while True:
            audio_data = await websocket.receive_bytes()

            # 2. Transcribe Audio (passing the market language to ASR)
            user_text = await asyncio.to_thread(transcribe_audio_bytes, audio_data, language=asr_lang)
            if not user_text:
                continue

            await websocket.send_json({"type": "transcript", "speaker": "User", "text": user_text})

            # 3. Concurrent Execution of Nudge and Agent (Solves the latency delay)
            nudge_task = asyncio.to_thread(nudge_engine.analyze_transcript_chunk, f"Customer: {user_text}")
            agent_task = asyncio.to_thread(orchestrator.process_message, user_text)

            nudge, agent_text = await asyncio.gather(nudge_task, agent_task)

            if nudge:
                await websocket.send_json({
                    "type": "nudge",
                    "signal": nudge.signal,
                    "text": nudge.nudge_text,
                    "confidence": nudge.confidence,
                    "priority": nudge.priority
                })

            # Safely check state (Checklist Item #3 notes that LocalizedVoiceAgent doesn't have a state machine yet)
            status = "N/A"
            missing_field = None
            if hasattr(orchestrator, "state"):
                status, _ = orchestrator.state.evaluate_eligibility()
                missing_field = orchestrator.state.get_missing_field()

            await websocket.send_json({
                "type": "transcript",
                "speaker": "Salita",
                "text": agent_text,
                "qualification_status": status,
                "missing_field": missing_field
            })

            # 4. Stream Audio Progressively (no full-buffer wait before the first byte reaches the client)
            await websocket.send_json({"type": "audio_start"})
            communicate = edge_tts.Communicate(agent_text, tts_voice)
            async for chunk in communicate.stream():
                if chunk["type"] == "audio":
                    await websocket.send_bytes(chunk["data"])
            await websocket.send_json({"type": "audio_end"})

    except WebSocketDisconnect:
        print(f"[WebSocket] Client disconnected from {market_code} market session.")