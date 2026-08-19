from orchestrator import LoanAgentOrchestrator

def run_agent_test():
    agent = LoanAgentOrchestrator()
    
    # Simulated multi-turn user conversation
    simulated_conversation = [
        "Hi, I'm interested in applying for a business loan. My name is Priya.",
        "I run a tech consulting firm. What documents do I need to prepare?",
        "Got it. We've been in business for 3 years.",
        "Our average monthly revenue is around 85,000 INR.",
        "We're looking for a loan of 500,000 INR for purchasing new server hardware.",
        "No, we don't have any past defaults on any loans."
    ]

    print("=========================================")
    print(" Q1 VOICE AGENT CONVERSATION TEST")
    print("=========================================\n")

    for turn, user_msg in enumerate(simulated_conversation, 1):
        print(f"User (Turn {turn}): {user_msg}")
        agent_reply = agent.process_message(user_msg)
        status, reason = agent.state.evaluate_eligibility()
        next_field = agent.state.get_missing_field()
        
        print(f"Salita: {agent_reply}")
        print(f"[State -> Status: {status} | Missing Field: {next_field}]")
        print("-" * 50 + "\n")

if __name__ == "__main__":
    run_agent_test()