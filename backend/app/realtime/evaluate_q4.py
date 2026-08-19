import time
import statistics
from signals import NudgeEngine

def run_q4_evaluation():
    print("=========================================")
    print(" Q4 REAL-TIME INSIGHTS & NUDGE EVALUATION")
    print("=========================================\n")

    # Cooldown set to 10 seconds for testing
    engine = NudgeEngine(confidence_threshold=0.70, cooldown_seconds=10.0)
    latencies = []

    # Streamed real-time transcript chunks
    simulated_stream = [
        {"speaker": "Customer", "text": "Hi, I wanted to check my application status for the business loan."},
        {"speaker": "Agent", "text": "Sure, let me check that for you."},
        {"speaker": "Customer", "text": "I've called three times this week and no one has gotten back to me! This service is terrible!"},  # Trigger: rising_frustration
        {"speaker": "Customer", "text": "Why is nobody answering my questions? This is completely unacceptable!"},                  # Duplicate: should suppress
        {"speaker": "Customer", "text": "Honestly, business has been slow and I'm really struggling to make my existing loan payments."}, # Trigger: payment_difficulty
        {"speaker": "Agent", "text": "I understand. We also have an equipment financing program available if you're buying hardware."},
        {"speaker": "Customer", "text": "Wait, what equipment program? You never mentioned that before!"}                         # Trigger: missed_cross_sell
    ]

    for turn, item in enumerate(simulated_stream, 1):
        chunk = f"{item['speaker']}: {item['text']}"
        print(f"[Chunk {turn}] {chunk}")
        
        t_start = time.perf_counter()
        nudge = engine.analyze_transcript_chunk(chunk)
        t_end = time.perf_counter()
        
        elapsed_ms = (t_end - t_start) * 1000
        latencies.append(elapsed_ms)

        if nudge:
            print(f" -> 🚨 [NUDGE GENERATED] ({nudge.priority}): {nudge.nudge_text}")
            print(f"    Signal: {nudge.signal} | Confidence: {nudge.confidence} | Latency: {nudge.latency_ms}ms")
        else:
            print(" -> [No Nudge Triggered / Suppressed]")
        
        print("-" * 60)
        time.sleep(0.5)  # Simulate real-time streaming pacing

    # --- Latency & Performance Report ---
    if latencies:
        latencies_sorted = sorted(latencies)
        p50 = statistics.median(latencies_sorted)
        # Calculate P95 index
        p95_idx = int(0.95 * len(latencies_sorted)) - 1
        p95 = latencies_sorted[max(0, p95_idx)]

        print("\n=========================================")
        print(" LATENCY & PERFORMANCE SUMMARY")
        print("=========================================")
        print(f"Total Chunks Analyzed : {len(latencies)}")
        print(f"P50 Latency (Median)  : {p50:.2f} ms")
        print(f"P95 Latency           : {p95:.2f} ms")
        print(f"Min Latency           : {min(latencies):.2f} ms")
        print(f"Max Latency           : {max(latencies):.2f} ms")
        print("=========================================")

if __name__ == "__main__":
    run_q4_evaluation()