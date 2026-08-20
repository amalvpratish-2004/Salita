# Salita

A knowledge-grounded, multi-market voice agent for business loan qualification — built for the
AI Engineer Assessment. Salita runs a live voice call over WebSocket (ASR → RAG-grounded LLM
agent → TTS), tracks applicant eligibility through a deterministic state machine, and surfaces
real-time coaching signals ("nudges") to a human agent while the call is in progress.

> **Status:** working prototype, not production-ready. See [Known Limitations](#known-limitations)
> below and [`docs/fix.md`](docs/fix.md) for the full, current list of gaps and open issues.

---

## What it does

| Pillar | What's implemented |
|---|---|
| **Q1 — Loan qualification agent** | State-machine-driven conversation (`LoanApplicationState`) that collects applicant details, enforces eligibility rules deterministically (not via LLM judgment), and gives a QUALIFIED / INCOMPLETE / DISQUALIFIED verdict each turn. |
| **Q2 — RAG knowledge base** | Ingestion pipeline (load → clean → mask PII → chunk → embed → store) over a synthetic business-loan document set, served through a retrieval API and injected into the agent's prompt for grounded answers. |
| **Q3 — Localized voice bots** | Market-configured personas for the Philippines (Taglish) and Indonesia (Bahasa Indonesia), with market-specific TTS voices and ASR language codes, selectable per call. |
| **Q4 — Real-time call insights** | A concurrent nudge engine that watches the live transcript for rising frustration, compliance gaps, missed cross-sell opportunities, and payment difficulty, with confidence thresholds and per-signal cooldowns to avoid nudge spam. |

---

## Architecture

```
frontend/index.html  ──(WebSocket audio + JSON)──►  backend/app/api/voice.py
                                                            │
                                    ┌───────────────────────┼───────────────────────┐
                                    ▼                       ▼                       ▼
                          backend/app/ai/asr.py   backend/app/agent/*      backend/app/realtime/*
                          (faster-whisper)         orchestrator.py          signals.py (NudgeEngine)
                                                    ├─ state.py (Q1 state machine)
                                                    └─ multilingual_agent.py (Q3)
                                                            │
                                                            ▼
                                                   backend/app/rag/*
                                                   (loader → cleaner → pii → chunker →
                                                    embeddings → ChromaDB → retriever)
                                                            │
                                                            ▼
                                                   backend/app/ai/llm.py
                                                   (Groq primary, Ollama local fallback)
                                                            │
                                                            ▼
                                                   backend/app/ai/tts.py / edge-tts
                                                   (streamed back to the client)
```

The WebSocket endpoint (`/ws/call`) is the primary integration point — it wires ASR, the
qualification/localization agent, the RAG-grounded prompt, the nudge engine, and streamed TTS
into a single live call loop. A parallel HTTP endpoint (`/agent/chat`) exposes the same
qualification agent as a text-only, session-keyed chat API.

---

## Repository structure

```
backend/
  app/
    agent/
      state.py              # Q1 eligibility state machine (source of truth for thresholds)
      qualification.py      # legacy/duplicate state machine — not wired in, kept for reference
      orchestrator.py        # Q1 conversation loop: extraction, RAG lookup, state transitions
      multilingual_agent.py  # Q3 localized persona (PH/ID)
      market_config.py       # Q3 market definitions: language, TTS voice, key terms, prompt
      evaluate_agent.py      # scripted multi-turn Q1 conversation test
      evaluate_q3.py         # scripted multi-turn Q3 conversation test
    ai/
      asr.py                 # faster-whisper transcription
      llm.py                 # Groq primary / Ollama fallback LLM client
      tts.py                 # edge-tts helper (file-based, used outside the live call path)
    api/
      agent.py                # POST /agent/chat — session-keyed text chat
      knowledge.py             # POST /knowledge/search — raw retrieval endpoint
      voice.py                 # WS /ws/call — the live voice call pipeline
    rag/
      loader.py               # .txt / .pdf / .csv ingestion
      cleaner.py               # whitespace/line normalization
      pii.py                   # regex-based PII masking (email, Indian mobile numbers)
      deduplicator.py          # exact-hash dedup (not currently called by ingest.py)
      chunker.py                # fixed-size character chunking
      metadata.py                # attaches source/chunk_id/document_type to each chunk
      embeddings.py               # sentence-transformers (all-MiniLM-L6-v2)
      vector_store.py              # ChromaDB helper (superseded by ingest.py's inline logic)
      ingest.py                     # end-to-end pipeline entry point
      retriever.py                   # top-k semantic search
      evaluate.py                     # scripted retrieval evaluation (5 test queries)
    realtime/
      signals.py               # Q4 NudgeEngine: signal detection, confidence gate, cooldown
      evaluate_q4.py             # scripted nudge-engine test with latency (p50/p95) reporting
    main.py                        # FastAPI app, route registration
data/
  synthetic/                       # source documents ingested into the knowledge base
docs/
  handover.md                      # internal architecture/technical handover notes
  fix.md                           # current, prioritized list of known gaps and required fixes
  AI_Engineer_Assessment_Master_Plan.md  # original planning document for this assessment
frontend/
  index.html                       # single-page live call UI (mic capture, transcript, nudges)
```

---

## Prerequisites

- Python 3.10+
- A [Groq](https://console.groq.com/) API key (primary LLM provider)
- [Ollama](https://ollama.com/) running locally (optional, but required for the LLM fallback path
  to actually work — without it, LLM calls simply fail if Groq is unavailable)
- A modern Chromium-based browser for the frontend (the live-playback audio path uses
  `MediaSource` with `audio/mpeg`, which isn't reliably supported in Safari — a non-streaming
  fallback is used there instead)

---

## Setup

```bash
git clone https://github.com/amalvpratish-2004/Salita.git
cd Salita

python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

pip install fastapi uvicorn[standard] httpx python-dotenv chromadb \
            sentence-transformers pypdf pandas pydantic faster-whisper edge-tts
```

> No `requirements.txt` is committed to the repo yet — the command above lists every third-party
> package actually imported by the codebase. Pin versions and commit a `requirements.txt` before
> treating this as reproducible for anyone else.

Create a `.env` file in the repo root:

```bash
GROQ_API_KEY=your_groq_api_key_here
GROQ_LLM_MODEL=openai/gpt-oss-20b     # optional, this is the default
OLLAMA_MODEL=qwen2.5:3b               # optional, this is the default
```

If you want the Ollama fallback to work, pull the model separately:

```bash
ollama pull qwen2.5:3b
```

(The Ollama endpoint itself is hardcoded to `http://localhost:11434/api/chat` in `llm.py` — not
currently configurable via `.env`.)

---

## Running

**1. Build the knowledge base** (run once, and again any time `data/synthetic/` changes):

```bash
cd backend
python app/rag/ingest.py
```

This populates a persistent ChromaDB store at `data/chroma/`.

**2. Start the API server:**

```bash
cd backend
uvicorn app.main:app --reload
```

The server starts at `http://localhost:8000`. `GET /` returns a basic health check.

**3. Open the frontend:**

Open `frontend/index.html` directly in a browser (no build step, no dev server needed). Grant
microphone access, pick a market region (English / Philippines / Indonesia), click **Start Live
Call**, then **Click to Speak** to record and send an utterance. The agent's reply text and voice
are synced to appear together on arrival, rather than the text appearing well before the audio.

---

## API reference

| Endpoint | Method | Description |
|---|---|---|
| `/` | GET | Health check |
| `/agent/chat` | POST | Text-only chat with the Q1 loan agent. Body: `{"message": "..."}`. Pass an `X-Session-Id` header to continue an existing session; omit it to start a new one (the response echoes back the `session_id` to reuse). |
| `/knowledge/search` | POST | Raw RAG retrieval. Body: `{"query": "...", "top_k": 2}`. Returns matched chunks with source/chunk metadata and distance scores. |
| `/ws/call` | WebSocket | Live voice call. Connect with `?market=EN\|PH\|ID`. Send raw audio bytes (webm/opus from `MediaRecorder`); receive a mix of JSON control messages (`transcript`, `nudge`, `audio_start`, `audio_end`) and binary TTS audio chunks. |

---

## Evaluation scripts

Each of these runs a scripted scenario and prints results to stdout — there's no automated
assertion/pass-fail harness yet, output needs to be read manually.

```bash
cd backend
python app/rag/evaluate.py           # 5 retrieval queries against the knowledge base
python app/agent/evaluate_agent.py   # one multi-turn Q1 qualifying conversation
python app/agent/evaluate_q3.py      # scripted PH and Indonesia conversations
python app/realtime/evaluate_q4.py   # nudge-engine test with p50/p95 latency reporting
```

---

## Known limitations

This section is deliberately honest — treat it as a task list, not a disclaimer.

- **Q3 has no knowledge grounding.** `multilingual_agent.py` calls the LLM directly with no RAG
  lookup, so PH/Indonesia answers to factual questions (fees, thresholds, document requirements)
  are generated, not retrieved. There's also no PH/Indonesia content in `data/synthetic/` yet.
- **The synthetic knowledge base is 2 documents**, not the 15–20 called for in the assessment —
  no deliberate duplicates, near-duplicates, or extraction-failure cases exist to exercise the
  cleaning/dedup stages.
- **`deduplicator.py` is never called** by `ingest.py` — dedup logic exists but doesn't run.
- **PII masking only catches two patterns** (email addresses, Indian 10-digit mobile numbers) —
  no coverage for names, addresses, government IDs, or PH/Indonesia phone formats.
- **`qualification.py` is dead code** — a legacy duplicate of the state machine in `state.py`,
  kept in the repo but not imported anywhere. Safe to delete once confirmed unused.
- **Chunking is fixed-size character slicing**, not sentence/paragraph-aware — can cut chunks
  mid-word.
- **No automated tests** — the `evaluate_*.py` scripts print scenario output for manual reading,
  not pass/fail assertions.

See [`docs/fix.md`](docs/fix.md) for the full prioritized list, including items already resolved
(session-keyed chat state, eligibility threshold consistency, concurrent nudge/agent execution,
streamed TTS playback).

---

## Documents

- [`docs/handover.md`](docs/handover.md) — architecture and component handover notes
- [`docs/fix.md`](docs/fix.md) — current prioritized fix/completion list
- [`docs/AI_Engineer_Assessment_Master_Plan.md`](docs/AI_Engineer_Assessment_Master_Plan.md) —
  original planning document