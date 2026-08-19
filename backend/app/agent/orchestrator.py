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

# Fallback wrapper in case retriever module is structured differently
try:
    from retriever import search_knowledge_base
except ImportError:
    def search_knowledge_base(query: str, top_k: int = 2):
        return []

class LoanAgentOrchestrator:
    def __init__(self):
        self.state = LoanApplicationState()
        self.conversation_history = []

    def extract_entities(self, user_message: str):
        """Uses structured LLM parsing to extract applicant attributes into state."""
        prompt = f"""Extract loan application details from the user's message.
Return ONLY a valid JSON object with these exact keys (use null if not mentioned):
- name (string or null)
- business_type (string or null)
- years_operating (integer or null)
- monthly_revenue (number or null)
- requested_amount (number or null)
- has_unresolved_default (boolean or null)

User Message: "{user_message}"
JSON:"""

        try:
            raw_json = generate_llm_response(prompt, temperature=0.0)
            match = re.search(r'\{.*\}', raw_json, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                for key, val in data.items():
                    if val is not None and hasattr(self.state, key):
                        if key == "years_operating":
                            val = int(val)
                        elif key in ["monthly_revenue", "requested_amount"]:
                            val = float(val)
                        elif key == "has_unresolved_default":
                            val = bool(val)
                        setattr(self.state, key, val)
        except Exception as e:
            print(f"[Entity Extraction Warning]: {e}")

    def process_message(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        # 1. Structured Entity Extraction
        self.extract_entities(user_message)

        # 2. Knowledge Base Search (RAG Context)
        rag_context = ""
        try:
            results = search_knowledge_base(user_message, top_k=2)
            if results:
                rag_context = "\n".join([
                    f"- {r.get('content', '')} [Source: {r.get('source', 'KB')}]" 
                    for r in results
                ])
        except Exception as e:
            print(f"[RAG Retrieval Warning]: {e}")

        # 3. Assess Qualification Requirements
        missing_field = self.state.get_missing_field()
        status, reason = self.state.evaluate_eligibility()

        # 4. Assemble Grounded Prompt
        system_prompt = f"""You are Salita, a professional AI business loan qualification agent.

Current Application State:
- Name: {self.state.name or 'Not provided'}
- Business Type: {self.state.business_type or 'Not provided'}
- Years Operating: {self.state.years_operating if self.state.years_operating is not None else 'Not provided'}
- Monthly Revenue: {self.state.monthly_revenue if self.state.monthly_revenue is not None else 'Not provided'}
- Requested Loan Amount: {self.state.requested_amount if self.state.requested_amount is not None else 'Not provided'}
- Unresolved Default: {self.state.has_unresolved_default if self.state.has_unresolved_default is not None else 'Not provided'}

Qualification Status: {status}
Next Missing Field Needed: {missing_field or 'None'}

Retrieved Knowledge Base Context:
{rag_context or 'No specific policy retrieved.'}

Instructions:
1. Speak naturally and concisely (1-2 short sentences maximum).
2. Never invent policies, interest rates, or applicant details.
3. If fields are missing, acknowledge any new info given and naturally request the Next Missing Field ({missing_field}).
4. If the applicant states their name, address them by name in subsequent turns.
"""

        response = generate_llm_response(user_message, system_prompt=system_prompt)
        self.conversation_history.append({"role": "assistant", "content": response})
        return response