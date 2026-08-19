from multilingual_agent import LocalizedVoiceAgent

def run_q3_evaluation():
    print("=========================================")
    print(" Q3 MULTILINGUAL VOICE BOT EVALUATION")
    print("=========================================\n")

    # 1. Test Philippines Market (Taglish)
    print("--- MARKET 1: PHILIPPINES (TAGLISH) ---")
    ph_agent = LocalizedVoiceAgent("PH")
    ph_scenarios = [
        "Hi po, I want to apply for a loan para sa retail business ko.",
        "Medyo mataas ba ang requirements? What documents do I need to prepare?",
        "Okay po, about fifty thousand monthly revenue naming shop. Pwede na ba 'yun?"
    ]

    for turn, msg in enumerate(ph_scenarios, 1):
        print(f"User (PH Turn {turn}): {msg}")
        reply = ph_agent.process_message(msg)
        print(f"Salita PH: {reply}\n")

    print("-" * 50 + "\n")

    # 2. Test Indonesia Market (Bahasa Indonesia)
    print("--- MARKET 2: INDONESIA (BAHASA INDONESIA) ---")
    id_agent = LocalizedVoiceAgent("ID")
    id_scenarios = [
        "Halo selamat siang, saya mau tanya soal pembiayaan usaha.",
        "Untuk cicilan per bulannya dan tenor paling lama berapa ya?",
        "Kalau misal jatuh tempo tapi ada keterlambatan, denda nya berapa?"
    ]

    for turn, msg in enumerate(id_scenarios, 1):
        print(f"User (ID Turn {turn}): {msg}")
        reply = id_agent.process_message(msg)
        print(f"Salita ID: {reply}\n")

if __name__ == "__main__":
    run_q3_evaluation()