import time
import json
import re
import sys
from pathlib import Path
from pydantic import BaseModel
from typing import Optional, List, Dict

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "ai"))

from llm import generate_llm_response

class Nudge(BaseModel):
    signal: str
    confidence: float
    evidence: str
    nudge_text: str
    priority: str  # HIGH, MEDIUM, LOW
    latency_ms: float

class NudgeEngine:
    def __init__(self, confidence_threshold: float = 0.70, cooldown_seconds: float = 20.0):
        self.confidence_threshold = confidence_threshold
        self.cooldown_seconds = cooldown_seconds
        self.last_triggered: Dict[str, float] = {}

    def analyze_transcript_chunk(self, transcript_chunk: str) -> Optional[Nudge]:
        t_start = time.perf_counter()

        system_prompt = """You are a real-time call monitoring AI analyzing an ongoing call transcript chunk.
Extract key signals if present:
1. missed_cross_sell (Agent forgot to mention an eligible product feature)
2. compliance_gap (Missing disclaimers or improper promises)
3. rising_frustration (Customer expressing anger, repetition, or annoyance)
4. payment_difficulty (Customer mentions inability to pay or debt stress)

Return ONLY a JSON object if a signal is detected, otherwise return {"signal": "none"}.
JSON Schema:
{
  "signal": "rising_frustration | compliance_gap | missed_cross_sell | payment_difficulty | none",
  "confidence": 0.85,
  "evidence": "Customer said: ...",
  "nudge_text": "Actionable 1-sentence guidance for agent",
  "priority": "HIGH | MEDIUM | LOW"
}"""

        raw_response = generate_llm_response(f"Transcript Chunk: {transcript_chunk}", system_prompt=system_prompt)
        t_end = time.perf_counter()
        latency_ms = round((t_end - t_start) * 1000, 2)

        try:
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)
            if not match:
                return None
            
            data = json.loads(match.group(0))
            signal = data.get("signal", "none")

            if signal == "none" or data.get("confidence", 0) < self.confidence_threshold:
                return None

            # --- Nudge Suppression & Cooldown Rules ---
            now = time.time()
            last_time = self.last_triggered.get(signal, 0)
            if (now - last_time) < self.cooldown_seconds:
                print(f"[Nudge Suppressed] Signal '{signal}' triggered within cooldown period ({round(now - last_time, 1)}s < {self.cooldown_seconds}s)")
                return None

            # Update cooldown timestamp
            self.last_triggered[signal] = now

            return Nudge(
                signal=signal,
                confidence=float(data["confidence"]),
                evidence=str(data["evidence"]),
                nudge_text=str(data["nudge_text"]),
                priority=str(data.get("priority", "MEDIUM")),
                latency_ms=latency_ms
            )

        except Exception as e:
            print(f"[Signal Detection Error]: {e}")
            return None

if __name__ == "__main__":
    engine = NudgeEngine()
    test_chunk = "I've called three times already and nobody is giving me a straight answer! This is ridiculous!"
    print("Testing Signal & Nudge Engine...")
    nudge = engine.analyze_transcript_chunk(test_chunk)
    if nudge:
        print(f"\n[Nudge Generated in {nudge.latency_ms}ms]:\nSignal: {nudge.signal}\nNudge: {nudge.nudge_text}\nConfidence: {nudge.confidence}")