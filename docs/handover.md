# Technical Handover Documentation: Salita AI System (Q1 & Q2)

## System Architecture Overview

* **RAG Knowledge Base Engine (Q2):** Ingestion pipeline with native loaders for `.txt`, `.pdf`, and `.csv` files. Text is scrubbed via regex-based PII masking, chunked, embedded using HuggingFace sentence-transformers, and indexed into a persistent ChromaDB store with source metadata.
* **Knowledge-Grounded Voice Agent (Q1):** State-machine-driven orchestrator (`LoanQualificationState`) enforcing policy rules ($\ge 2$ years operating, $\ge 50,000$ INR monthly revenue, zero unresolved defaults). Utilizes structured JSON extraction via LLM to parse user entities across dialogue turns.
* **LLM Engine & Resilience:** Primary integration with Groq API for low-latency text generation, backed by automatic fallback to local Ollama (`qwen2.5:3b`) on network or authentication failure.

---

## Component Matrix

| Module | Core Files | Responsibility |
| --- | --- | --- |
| **Ingestion Pipeline** | `backend/app/rag/loader.py`<br>

<br>`backend/app/rag/cleaner.py`<br>

<br>`backend/app/rag/pii.py`<br>

<br>`backend/app/rag/ingest.py` | Multi-format parsing, sanitization, PII masking, vector embedding, and ChromaDB persistence. |
| **Retrieval Engine** | `backend/app/rag/retriever.py`<br>

<br>`backend/app/rag/evaluate.py` | Top-$k$ context retrieval with metadata citation, and retrieval evaluation testing. |
| **State Machine** | `backend/app/agent/qualification.py` | Deterministic eligibility checking and tracking of missing required fields. |
| **Orchestrator** | `backend/app/agent/orchestrator.py`<br>

<br>`backend/app/agent/evaluate_agent.py` | Entity extraction, state transition execution, prompt assembly with RAG context, and multi-turn dialogue simulation. |
| **API Endpoints** | `backend/app/main.py`<br>

<br>`backend/app/api/agent.py`<br>

<br>`backend/app/api/knowledge.py` | FastAPI routes providing `/agent/chat` and `/knowledge/search` endpoints. |

---

## Key Technical Decisions

* **Deterministic Qualification:** Loan criteria enforcement is handled strictly via Python logic rather than LLM prompts to eliminate policy hallucination risks.
* **Source Citation:** Knowledge Base context injections carry source document tags (e.g., `[Source: loan_eligibility.txt]`), enabling transparent grounding.
* **Fault-Tolerant Resilience:** LLM execution uses retry and fallback wrappers (`Groq` $\rightarrow$ `Ollama`) to prevent call drops during upstream provider issues.

---

## Operations & Verification Guide

1. **Re-index Knowledge Base:**
```bash
python backend/app/rag/ingest.py

```


2. **Execute RAG Retrieval Suite:**
```bash
python backend/app/rag/evaluate.py

```


3. **Execute Agent Multi-turn Test:**
```bash
python backend/app/agent/evaluate_agent.py

```


4. **Launch Application API:**
```bash
cd backend
uvicorn app.main:app --reload

```



---