import sys
from pathlib import Path

# Add paths for imports
current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "ai"))

from llm import generate_llm_response
from market_config import get_market_config, MarketConfig

class LocalizedVoiceAgent:
    def __init__(self, market_code: str):
        self.config: MarketConfig = get_market_config(market_code)
        self.conversation_history = []

    def process_message(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        system_prompt = f"""{self.config.system_instruction}

Market Sector: {self.config.sector}
Key Terminology Mapping:
{self.config.key_terms}

Response Guidelines:
1. Respond naturally in {self.config.primary_language}.
2. Maintain appropriate market register and politeness.
3. Keep response under 3 concise sentences for clear text-to-speech rendering.
4. Adapt naturally to the user's input rather than providing literal line-by-line translations.
"""

        response = generate_llm_response(user_message, system_prompt=system_prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response

if __name__ == "__main__":
    agent_ph = LocalizedVoiceAgent("PH")
    reply = agent_ph.process_message("Magkano po ang kailangan para sa business loan?")
    print(f"[PH Agent Reply]:\n{reply}")