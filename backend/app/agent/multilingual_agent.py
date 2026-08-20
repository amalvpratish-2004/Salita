import os
import sys
import json
from pathlib import Path
from typing import Tuple, Optional
from google import genai

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "ai"))
sys.path.append(str(backend_dir / "app" / "rag"))
sys.path.append(str(backend_dir / "app" / "agent"))

from market_config import get_market_config
from retriever import KBRetriever
from state import ApplicationState  # Qualification State Tracker


class LocalizedVoiceAgent:
    def __init__(self, market_code: str = "PH"):
        self.market_code = market_code.upper()
        self.config = get_market_config(self.market_code)
        self.retriever = KBRetriever()
        self.state = ApplicationState()  # Connects eligibility state machine

        api_key = os.getenv("GEMINI_API_KEY")
        self.client = genai.Client(api_key=api_key) if api_key else None

    def _extract_slots_and_respond(self, user_text: str, context: str) -> str:
        """Extracts slot data (revenue, tenure, defaults) while generating localized response."""
        system_prompt = f"""{self.config.system_instruction}

Knowledge Base Grounding Context:
{context if context else 'No specific document retrieved.'}

Key Financial Terminology Reference:
{self.config.key_terms}

Current Known State of Applicant:
- Monthly Revenue: {self.state.monthly_revenue or 'Unknown'}
- Business Tenure Years: {self.state.business_tenure_years or 'Unknown'}
- Active Defaults: {self.state.has_defaults if self.state.has_defaults is not None else 'Unknown'}

Instructions:
1. Extract any financial variables mentioned by the customer.
2. Formulate a conversational response in {self.config.primary_language} answering their question or asking for missing eligibility information.
3. Output MUST be valid JSON with two fields:
   "extracted": {{"monthly_revenue": int or null, "business_tenure_years": float or null, "has_defaults": bool or null}},
   "response": "Your spoken conversational response"
"""

        if not self.client:
            return f"[Mock {self.market_code}] Maraming salamat po! Regarding '{user_text}', we require 2 years business history."

        try:
            res = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[
                    {"role": "user", "parts": [{"text": system_prompt + f"\n\nCustomer: {user_text}"}]}
                ]
            )
            raw = res.text.strip()
            # Clean markdown JSON block if present
            if "```json" in raw:
                raw = raw.split("```json")[1].split("```")[0].strip()
            elif "```" in raw:
                raw = raw.split("```")[1].split("```")[0].strip()

            parsed = json.loads(raw)

            # Update state with extracted slots
            extracted = parsed.get("extracted", {})
            if extracted.get("monthly_revenue"):
                self.state.monthly_revenue = float(extracted["monthly_revenue"])
            if extracted.get("business_tenure_years"):
                self.state.business_tenure_years = float(extracted["business_tenure_years"])
            if extracted.get("has_defaults") is not None:
                self.state.has_defaults = bool(extracted["has_defaults"])

            return parsed.get("response", raw)

        except Exception as e:
            print(f"[Agent Extraction Error] {e}")
            return "Pasensya na po, paki-ulit lang po ng inyong katanungan."

    def process_message(self, user_text: str) -> str:
        # 1. Retrieve market-filtered knowledge chunks
        context = self.retriever.query(user_text, market_code=self.market_code, top_k=2)

        # 2. Extract slots and generate localized agent response
        return self._extract_slots_and_respond(user_text, context)