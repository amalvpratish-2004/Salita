import os
import httpx
from pathlib import Path
from dotenv import load_dotenv

# Ensure .env is loaded from the project root regardless of execution path
current_dir = Path(__file__).resolve().parent
salita_root = current_dir.parent.parent.parent
load_dotenv(salita_root / ".env")

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = os.getenv("GROQ_LLM_MODEL", "openai/gpt-oss-20b")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_URL = "http://localhost:11434/api/chat"

def query_groq(prompt, system_prompt="You are a helpful AI assistant."):
    """Primary LLM call to Groq API with detailed error capture."""
    if not GROQ_API_KEY or "your_groq_api_key" in GROQ_API_KEY:
        raise ValueError("Valid GROQ_API_KEY is not configured in .env")

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.2
    }

    response = httpx.post(url, headers=headers, json=payload, timeout=10.0)
    
    if response.status_code != 200:
        raise RuntimeError(f"Groq API Error ({response.status_code}): {response.text}")

    data = response.json()
    return data["choices"][0]["message"]["content"]

def query_ollama(prompt, system_prompt="You are a helpful AI assistant."):
    """Fallback LLM call to local Ollama instance."""
    payload = {
        "model": OLLAMA_MODEL,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt}
        ],
        "stream": False
    }

    response = httpx.post(OLLAMA_URL, json=payload, timeout=30.0)
    response.raise_for_status()
    data = response.json()
    return data["message"]["content"]

def generate_llm_response(prompt, system_prompt="You are a helpful AI assistant."):
    """Tries Groq first; falls back to local Ollama if Groq fails."""
    try:
        return query_groq(prompt, system_prompt)
    except Exception as e:
        print(f"[LLM Warning] Groq unavailable ({e}). Switching to Ollama local fallback...")
        try:
            return query_ollama(prompt, system_prompt)
        except Exception as ollama_err:
            print(f"[LLM Error] Ollama fallback also failed: {ollama_err}")
            return "I apologize, but I am currently experiencing technical difficulty processing your request."

if __name__ == "__main__":
    test_prompt = "Say hello and confirm you are online in 1 short sentence."
    print("Testing LLM Service...")
    response = generate_llm_response(test_prompt)
    print(f"\nResponse:\n{response}")