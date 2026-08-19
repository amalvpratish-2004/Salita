import sys
import json
import re
from pathlib import Path

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "ai"))
sys.path.append(str(backend_dir / "app" / "rag"))

from state import LoanApplicationState
from llm import generate_llm_response

try:
    from retriever import search_knowledge_base
except ImportError:
    def search_knowledge_base(query: str, top_k: int = 2):
        return []

class LoanAgentOrchestrator:
    def __init__(self):
        self.state = LoanApplicationState()
        self.conversation_history = []
        self.is_completed = False

    def process_message(self, user_message: str) -> str:
        # If application was already finalized in a previous turn
        if self.is_completed:
            closing_reply = f"Thank you, {self.state.name or 'there'}! Your application has already been processed. Our team will contact you directly."
            self.conversation_history.append({"role": "assistant", "content": closing_reply})
            return closing_reply

        self.conversation_history.append({"role": "user", "content": user_message})

        # 1. Selective RAG context lookup
        rag_context = ""
        msg_lower = user_message.lower()
        if any(w in msg_lower for w in ["what", "how", "why", "policy", "interest", "rate", "limit", "eligible"]):
            try:
                results = search_knowledge_base(user_message, top_k=1)
                if results:
                    rag_context = "\n".join([f"- {r.get('content', '')}" for r in results])
            except Exception as e:
                print(f"[RAG Retrieval Warning]: {e}")

        missing_field = self.state.get_missing_field()
        status, reason = self.state.evaluate_eligibility()

        # 2. Single-pass LLM extraction and conversational turn
        system_prompt = """You are Salita, a concise AI business loan qualification agent.

STRICT INSTRUCTIONS:
1. Extract any newly provided applicant details from the User Message.
2. Formulate a natural, 1-2 sentence response asking ONLY for the Next Missing Field.
3. Respond strictly in valid JSON format matching this schema:
{
  "extracted": {
    "name": string or null,
    "business_type": string or null,
    "years_operating": integer or null,
    "monthly_revenue": number or null,
    "requested_amount": number or null,
    "has_unresolved_default": boolean or null
  },
  "response": "Your short 1-2 sentence agent response here."
}"""

        user_prompt = f"""Current State: {self.state.model_dump_json()}
Qualification Status: {status}
Next Missing Field: {missing_field or 'None'}
Policy Context: {rag_context or 'None'}

User Message: "{user_message}" """

        agent_response = ""
        try:
            raw_response = generate_llm_response(user_prompt, system_prompt=system_prompt)
            raw_response = raw_response.replace("```json", "").replace("```", "").strip()
            match = re.search(r'\{.*\}', raw_response, re.DOTALL)

            if match:
                data = json.loads(match.group(0))
                extracted = data.get("extracted", {})

                # Update application state
                for key, val in extracted.items():
                    if val is not None and hasattr(self.state, key):
                        if getattr(self.state, key) is None:
                            setattr(self.state, key, val)

                agent_response = data.get("response", "")
        except Exception as e:
            print(f"[Orchestrator Error]: {e}")

        # 3. Post-extraction state re-evaluation
        status, reason = self.state.evaluate_eligibility()
        next_missing = self.state.get_missing_field()

        # 4. Trigger terminal ending message if Qualified or Rejected
        if status == "DISQUALIFIED":
            self.is_completed = True
            agent_response = f"Thank you for providing your information, {self.state.name or 'applicant'}. Based on our underwriting criteria ({reason}), we cannot proceed with your loan application at this time."
        elif status == "QUALIFIED" or next_missing is None:
            self.is_completed = True
            agent_response = f"Congratulations {self.state.name or ''}! You are preliminarily qualified for the loan. Our underwriting team will contact you shortly to finalize the details."
        elif not agent_response:
            agent_response = f"Got it. Could you please share your {next_missing.replace('_', ' ')}?"

        self.conversation_history.append({"role": "assistant", "content": agent_response})
        return agent_response