# Salita — Fix & Completion List

Generated from a direct code review of `amalvpratish-2004/Salita` (main branch). Organized by
priority. Each item names the exact file(s) involved and what "done" looks like.

---

## P0 — Correctness bugs (fix before anything else; these make current claims false)

### 1. Two contradictory eligibility engines — wrong one is wired in
- **Files:** `backend/app/agent/state.py`, `backend/app/agent/qualification.py`, `backend/app/agent/orchestrator.py`
- **Problem:** `orchestrator.py` imports `LoanApplicationState` from `state.py` (thresholds: 1 year
  operating, ₹10,000/month revenue). `qualification.py` defines a second class, `LoanQualificationState`,
  with different thresholds (2 years, ₹50,000/month) that match both `docs/handover.md` and the
  ingested policy document (`data/synthetic/loan_eligibility.txt`). `qualification.py` is never
  imported anywhere except its own `__main__` block — it's dead code.
- **Fix:**
  - [ ] Delete one of the two classes. Keep a single source of truth for eligibility logic.
  - [ ] The surviving class's thresholds must exactly match the numbers in the ingested policy
        document — don't hardcode a second copy of the numbers; either read them from the KB at
        startup or add a test that fails if they diverge.
  - [ ] Add `loan_purpose` and `human_escalation_requested` fields to whichever state class survives
        — `state.py` currently drops both, even though `orchestrator.py`'s missing-field flow implies
        `loan_purpose` should be collected.
  - [ ] Add a regression test with a borderline applicant (e.g., 1.5 years, ₹30,000/month) that must
        return DISQUALIFIED. This is the exact case the current bug gets wrong.

### 2. Shared global orchestrator across all HTTP callers
- **File:** `backend/app/api/agent.py`
- **Problem:** `orchestrator = LoanAgentOrchestrator()` is instantiated once at module load and reused
  for every request. Two concurrent users will read and overwrite each other's conversation state.
- **Fix:**
  - [ ] Key orchestrator instances by session/connection ID (a dict keyed by a session token from the
        client, or move fully to the WebSocket flow where each connection gets its own instance, as
        `voice.py` already does correctly).

---

## P0 — Missing pillar: Q3 is not a working localized voice bot

### 3. Q3 has no knowledge grounding
- **File:** `backend/app/agent/multilingual_agent.py`
- **Problem:** `LocalizedVoiceAgent.process_message` calls `generate_llm_response` directly with no
  RAG lookup. It will answer factual questions (revenue thresholds, late fees, document
  requirements) by guessing, not by retrieval — the exact failure mode Q1/Q2 were built to avoid.
- **Fix:**
  - [ ] Import and call `search_knowledge_base` (or a market-scoped variant, see #4) inside
        `process_message`, inject retrieved context into the prompt, same pattern as `orchestrator.py`.
  - [ ] Add a qualification/state layer for Q3 (or reuse the Q1 state machine with market-specific
        thresholds) — currently Q3 has no structured qualification tracking at all, just free chat.

### 4. No PH or Indonesia source material exists
- **Files:** `data/synthetic/` (only 2 English/INR files currently exist)
- **Fix:**
  - [ ] Create a PH knowledge set: life insurance/bancassurance eligibility, premiums, coverage,
        required documents — in English/Filipino/Taglish as appropriate.
  - [ ] Create an Indonesia knowledge set: multifinance/consumer finance eligibility, cicilan/tenor/DP
        terms, late fee (denda) policy — in Bahasa Indonesia.
  - [ ] Tag each chunk with `market_code` metadata (`PH` / `ID` / default) in `metadata.py` so
        retrieval can be scoped per market and PH content doesn't leak into an Indonesia call or
        vice versa.
  - [ ] Re-run ingestion and confirm `retriever.py` supports a market filter (Chroma `where` clause
        on metadata) — currently `search_knowledge_base` has no market parameter at all.

### 5. Q3 is not connected to voice (ASR/TTS/WebSocket)
- **File:** `backend/app/api/voice.py`
- **Problem:** `/ws/call` hard-codes `LoanAgentOrchestrator` and the `en-US-AriaNeural` TTS voice.
  `LocalizedVoiceAgent` and the PH/Indonesia voices defined in `market_config.py` are never used
  inside the actual voice pipeline — Q3 only runs as a standalone text script (`evaluate_q3.py`).
- **Fix:**
  - [ ] Accept a `market_code` parameter on WebSocket connect (e.g. query param `?market=PH`).
  - [ ] Route to `LocalizedVoiceAgent` (now grounded, per #3/#4) when market_code is PH/ID, else the
        existing English loan orchestrator.
  - [ ] Use `market_config.py`'s `tts_voice_male` / `tts_voice_female` instead of the hard-coded
        `en-US-AriaNeural`.
  - [ ] Confirm `faster-whisper`'s `transcribe_audio_bytes` is called with the right `language` param
        per market (currently always defaults to `"en"` — will mis-transcribe Taglish/Bahasa input).

---

## P1 — High: undermines specific claims already being made

### 6. Deduplication is built but never runs
- **File:** `backend/app/rag/ingest.py`, `backend/app/rag/deduplicator.py`
- **Fix:** `[ ]` Call `remove_duplicates` (or a near-duplicate variant, see #8) inside
  `process_directory()` before chunking/embedding. Right now it only runs in its own `__main__` demo.

### 7. Synthetic corpus is 2 files, not the required 15–20
- **File:** `data/synthetic/`
- **Fix:**
  - [ ] Expand to 15–20 English business-loan documents covering: product/marketing, current
        eligibility policy, a **deliberately stale/superseded** duplicate version, loan limits/pricing
        tables, required-documents checklist, FAQ, objection-handling guide, application process,
        business-type restrictions, revenue verification rules, existing-debt rules, disclosures/
        compliance, escalation policy, callback policy.
  - [ ] Include at least one **near-duplicate** doc (reworded, not byte-identical) to test dedup
        beyond exact-hash matching (current `deduplicator.py` only does SHA-256 exact match — will
        miss reworded duplicates entirely).
  - [ ] Include at least one doc with a genuine **extraction/formatting problem** (garbled text,
        broken table) so the cleaning stage has something real to catch.
  - [ ] Include the existing PII example, but expand `pii.py` coverage first (#9) so it's actually
        caught end-to-end.
  - [ ] Exercise the PDF and CSV loaders (`loader.py` supports both but neither is currently tested
        against a real file in the corpus) — add at least one real `.pdf` and one `.csv`.

### 8. Exact-hash-only deduplication will miss near-duplicates
- **File:** `backend/app/rag/deduplicator.py`
- **Fix:** `[ ]` Add a near-duplicate check (e.g. cosine similarity on embeddings above a threshold,
  or a shingling/MinHash approach) in addition to the existing exact-hash check. Document the
  threshold you choose and why.

### 9. PII masking only catches 2 patterns
- **File:** `backend/app/rag/pii.py`
- **Fix:**
  - [ ] Add patterns/NER for: full names, physical addresses, government ID numbers, bank account
        numbers.
  - [ ] Add PH and Indonesia phone number formats (current regex is India-only, 10-digit `[6-9]`
        prefix).
  - [ ] Decide and document a policy: mask-and-keep vs. flag-and-exclude entire documents containing
        PII from retrieval. Currently everything is silently masked and indexed regardless.

### 10. No README, requirements.txt, or .env.example
- **Repo root**
- **Fix:**
  - [ ] Add `requirements.txt` (or `pyproject.toml`) pinning every dependency actually imported:
        `fastapi`, `uvicorn`, `httpx`, `python-dotenv`, `chromadb`, `sentence-transformers`, `pypdf`,
        `pandas`, `pydantic`, `faster-whisper`, `edge-tts`.
  - [ ] Add `.env.example` listing `GROQ_API_KEY`, `GROQ_LLM_MODEL`, `OLLAMA_MODEL`.
  - [ ] Add a top-level `README.md`: what the project is, how to install, how to run ingestion, how
        to launch the API, how to hit the WebSocket. `docs/handover.md` is a good internal doc but
        isn't a substitute for a reproducible setup guide.

---

## P2 — Medium: real gaps, survivable for a prototype demo but worth fixing

### 11. Character-count chunking cuts words/sentences mid-token
- **File:** `backend/app/rag/chunker.py`
- **Fix:** `[ ]` Switch to sentence- or paragraph-aware chunking (split on sentence boundaries, then
  pack up to the size limit) so citations and retrieved text read cleanly.

### 12. Sequential double-LLM-call per voice turn
- **File:** `backend/app/api/voice.py`
- **Problem:** Every turn calls the nudge engine (`analyze_transcript_chunk`) and then the
  orchestrator (`process_message`) sequentially — two full LLM round-trips per user utterance,
  each with up to a 10s Groq timeout before a 30s Ollama fallback.
- **Fix:**
  - [ ] Run nudge detection and agent response generation concurrently (`asyncio.gather`) instead of
        sequentially, since they don't depend on each other's output.
  - [ ] Consider a cheap local pre-filter (keyword/regex heuristic) before invoking the LLM for nudge
        detection, so most turns skip the second LLM call entirely.

### 13. Eligibility thresholds hardcoded separately from the policy document
- **File:** `backend/app/agent/state.py` (or `qualification.py`, whichever survives #1)
- **Fix:** `[ ]` At minimum, add an automated check that fails CI/tests if the hardcoded thresholds
  don't match the numbers in `data/synthetic/loan_eligibility.txt`. Longer-term: consider deriving
  thresholds from a small structured policy config file that both the code and the ingested document
  are generated from, so they can't drift.

### 14. No escalation or callback logic actually implemented
- **Files:** `backend/app/agent/orchestrator.py`, `backend/app/agent/qualification.py`
- **Problem:** `human_escalation_requested` exists as a field name in `qualification.py` but is never
  read or set anywhere. There's no code path that detects an escalation trigger, logs it, or responds
  to a callback request, despite this being a named requirement.
- **Fix:**
  - [ ] Detect escalation triggers (explicit request, out-of-KB question, dispute/complaint,
        compliance-sensitive statement) in `orchestrator.py`.
  - [ ] Add a callback-request path: capture preferred time window, contact number, reason — and log
        it (even just to a file/DB row for the prototype).
  - [ ] Wire these into the WebSocket/API response so the frontend can display escalation state.

### 15. Testing is happy-path only
- **Files:** `backend/app/agent/evaluate_agent.py`, `backend/app/agent/evaluate_q3.py`
- **Fix:**
  - [ ] Add a disqualification scenario (fails an eligibility rule).
  - [ ] Add an escalation scenario (explicit human request, or out-of-KB question).
  - [ ] Add an objection-handling scenario (price pushback, reluctance to share documents).
  - [ ] Bring the total up to the assessment's "5 recorded test calls" — happy path is currently the
        only case exercised, and it's the one case that can't expose the P0 bug in #1.

### 16. Repo hygiene
- **File:** `backend/temp_agent_response.mp3` (committed binary artifact)
- **Fix:** `[ ]` Remove it, add `*.mp3` to `.gitignore`.

---

## Suggested order of work

1. Fix #1 and #2 (correctness bugs — these make the demo lie about its own behavior).
2. Build out #4 (PH/Indonesia source material) and #3 (ground Q3 in RAG).
3. Wire #5 (connect Q3 to the actual voice WebSocket) — without this, Q3 doesn't exist as a "voice
   bot" in any demoable sense.
4. Expand the corpus (#7), wire dedup (#6), strengthen PII (#9).
5. Add README/requirements/.env.example (#10) — cheap, high value for anyone trying to run this.
6. Everything in P2 as time allows; #12 (latency) and #15 (test coverage) are the highest-value of
   the remaining items if time is short.