from pydantic import BaseModel
from typing import Dict, List

class MarketConfig(BaseModel):
    market_code: str
    country: str
    sector: str
    primary_language: str
    supported_locales: List[str]
    tts_voice_male: str
    tts_voice_female: str
    key_terms: Dict[str, str]
    system_instruction: str

# 1. Philippines Market Configuration (Taglish)
PHILIPPINES_CONFIG = MarketConfig(
    market_code="PH",
    country="Philippines",
    sector="Life Insurance / Business Lending",
    primary_language="Taglish",
    supported_locales=["en-PH", "tl-PH"],
    tts_voice_male="fil-PH-AngeloNeural",
    tts_voice_female="fil-PH-BlessicaNeural",
    key_terms={
        "premium": "premium / hulog",
        "policy": "policy / kontrata",
        "coverage": "coverage / proteksyon",
        "beneficiary": "beneficiary / tagapag-mana",
        "monthly_revenue": "monthly revenue / kita buwan-buwan"
    },
    system_instruction="""You are Salita, a friendly customer agent speaking natural Taglish (a blend of English and Tagalog).
Guidelines:
1. Mix Tagalog and English naturally as spoken in Manila business contexts (e.g., "Para sa loan application ninyo, we need to check your monthly revenue.").
2. Keep sentences polite using "po" and "opo" where appropriate.
3. Keep responses concise (1-3 short sentences).
4. Do not translate financial terms like 'monthly revenue', 'loan amount', or 'bank statements' literally; use common English financial terms mixed into Tagalog phrasing."""
)

# 2. Indonesia Market Configuration (Bahasa Indonesia)
INDONESIA_CONFIG = MarketConfig(
    market_code="ID",
    country="Indonesia",
    sector="Multifinance / Consumer Finance",
    primary_language="Bahasa Indonesia",
    supported_locales=["id-ID"],
    tts_voice_male="id-ID-ArdiNeural",
    tts_voice_female="id-ID-GadisNeural",
    key_terms={
        "installment": "cicilan / angsuran",
        "tenor": "tenor / jangka waktu",
        "down_payment": "DP / uang muka",
        "due_date": "jatuh tempo",
        "penalty": "denda"
    },
    system_instruction="""You are Salita, a professional customer agent speaking natural Bahasa Indonesia.
Guidelines:
1. Use polite, conversational Bahasa Indonesia suitable for financial services (e.g., "Selamat siang, bisa dibantu untuk pengajuan pembiayaannya?").
2. Incorporate common financial loanwords naturally (e.g., cicilan, tenor, DP, jatuh tempo).
3. Keep responses concise (1-3 short sentences).
4. Handle both formal and colloquial phrasing gracefully without losing professional politeness."""
)

def get_market_config(market_code: str) -> MarketConfig:
    """Helper selector for active market configuration."""
    code = market_code.upper()
    if code == "PH":
        return PHILIPPINES_CONFIG
    elif code == "ID":
        return INDONESIA_CONFIG
    else:
        raise ValueError(f"Unsupported market code: {market_code}. Choose 'PH' or 'ID'.")

if __name__ == "__main__":
    ph = get_market_config("PH")
    id_cfg = get_market_config("ID")
    print(f"Loaded Market {ph.country}: Voice = {ph.tts_voice_female}")
    print(f"Loaded Market {id_cfg.country}: Voice = {id_cfg.tts_voice_male}")