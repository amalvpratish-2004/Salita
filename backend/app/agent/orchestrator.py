import sys
import json
import re
from pathlib import Path

current_dir = Path(__file__).resolve().parent
backend_dir = current_dir.parent.parent
sys.path.append(str(backend_dir / "app" / "rag"))
sys.path.append(str(backend_dir / "app" / "ai"))

from retriever import search_knowledge_base
from llm import generate_llm_response
from qualification import LoanQualificationState

class LoanAgentOrchestrator:
    def __init__(self):
        self.state = LoanQualificationState()
        self.conversation_history = []

    def _extract_entities(self, user_message: str):
        """Extracts loan applicant parameters from the user's message using the LLM."""
        extraction_prompt = f"""Extract any loan application parameters mentioned in this message: "{user_message}"

Current Known State:
- name: {self.state.name}
- business_type: {self.state.business_type}
- years_operating: {self.state.years_operating}
- monthly_revenue: {self.state.monthly_revenue}
- loan_amount: {self.state.loan_amount}
- loan_purpose: {self.state.loan_purpose}
- has_unresolved_default: {self.state.has_unresolved_default}

Return ONLY a valid JSON object with extracted values. Use null for unmentioned fields. 
Numbers must be numeric integers or floats (e.g. 50000, 3). Booleans must be true/false.
Example output format:
{{"name": "Alex", "business_type": "Retail", "years_operating": null, "monthly_revenue": null, "loan_amount": null, "loan_purpose": null, "has_unresolved_default": null}}"""

        try:
            raw_json = generate_llm_response(user_message, system_prompt=extraction_prompt)
            # Find JSON block in LLM response
            match = re.search(r'\{.*\}', raw_json, re.DOTALL)
            if match:
                data = json.loads(match.group(0))
                if data.get("name") and not self.state.name:
                    self.state.name = str(data["name"])
                if data.get("business_type") and not self.state.business_type:
                    self.state.business_type = str(data["business_type"])
                if data.get("years_operating") is not None and self.state.years_operating is None:
                    self.state.years_operating = float(data["years_operating"])
                if data.get("monthly_revenue") is not None and self.state.monthly_revenue is None:
                    self.state.monthly_revenue = float(data["monthly_revenue"])
                if data.get("loan_amount") is not None and self.state.loan_amount is None:
                    self.state.loan_amount = float(data["loan_amount"])
                if data.get("loan_purpose") and not self.state.loan_purpose:
                    self.state.loan_purpose = str(data["loan_purpose"])
                if data.get("has_unresolved_default") is not None and self.state.has_unresolved_default is None:
                    self.state.has_unresolved_default = bool(data["has_unresolved_default"])
        except Exception as e:
            print(f"[Orchestrator Warning] Entity extraction failed: {e}")

    def process_message(self, user_message: str) -> str:
        self.conversation_history.append({"role": "user", "content": user_message})

        # 1. Update State Machine via Entity Extraction
        self._extract_entities(user_message)

        # 2. Retrieve Knowledge Base context if user asks a question
        kb_context = ""
        keywords = ["what", "how", "can", "document", "rate", "eligible", "requirement", "policy", "default"]
        if "?" in user_message or any(kw in user_message.lower() for kw in keywords):
            kb_results = search_knowledge_base(user_message, top_k=2)
            if kb_results.get("documents") and len(kb_results["documents"][0]) > 0:
                docs = kb_results["documents"][0]
                sources = kb_results["metadatas"][0]
                kb_context = "\n".join([f"[Source: {sources[i]['source']}] {docs[i]}" for i in range(len(docs))])

        # 3. Evaluate Qualification State
        status, reason = self.state.evaluate_eligibility()
        missing_field = self.state.get_missing_field()

        # 4. Construct Prompt & Generate Response
        system_prompt = f"""You are Salita, an empathetic and professional voice agent for business loan qualification.

Applicant Details:
- Name: {self.state.name}
- Business Type: {self.state.business_type}
- Years Operating: {self.state.years_operating}
- Monthly Revenue: {self.state.monthly_revenue}
- Loan Amount: {self.state.loan_amount}
- Loan Purpose: {self.state.loan_purpose}
- Has Unresolved Default: {self.state.has_unresolved_default}

Qualification Status: {status} ({reason})
Next Needed Field: {missing_field}

Retrieved Knowledge Context:
{kb_context if kb_context else 'No KB context retrieved.'}

Voice Agent Guidelines:
1. Speak concisely and conversationally (1-3 sentences max per output).
2. Ask for the next missing field: {missing_field}.
3. If Knowledge Context is provided, answer accurately citing policy guidelines.
"""

        llm_response = generate_llm_response(user_message, system_prompt=system_prompt)
        self.conversation_history.append({"role": "assistant", "content": llm_response})
        return llm_response