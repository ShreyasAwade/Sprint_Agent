import os
import time
import json
from typing import Tuple, Dict, Any

from groq import Groq
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize client
client = Groq(api_key=os.getenv("SPRINT_AGENT_API_KEY"))

# Configurable model
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

SYSTEM_PROMPT = """You are a helpful assistant.
Return concise, structured responses.
"""


# -----------------------
# LLM Call Wrapper (IMPORTANT)
# -----------------------
def call_llm(messages):
    try:
        response = client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.2,
        )
        return response
    except Exception as e:
        raise RuntimeError(f"LLM call failed: {str(e)}")


# -----------------------
# Baseline Model Run
# -----------------------
def run_baseline(feature: str) -> Tuple[str, int]:
    start = time.time()

    response = call_llm([
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": feature}
    ])

    latency_ms = int((time.time() - start) * 1000)

    raw_output = response.choices[0].message.content

    return raw_output, latency_ms


# -----------------------
# Agent Run
# -----------------------
def run_agent(feature: str) -> Tuple[Dict[str, Any], int]:
    from agent.core import SprintAgent  # local import to avoid circular deps

    agent = SprintAgent()

    start = time.time()

    try:
        plan = agent.plan(feature)
    except Exception as e:
        raise RuntimeError(f"Agent failed: {str(e)}")

    latency_ms = int((time.time() - start) * 1000)

    return plan, latency_ms


# -----------------------
# Benchmark Runner
# -----------------------
def run_benchmark(feature: str):
    print("\nRunning Benchmark...\n")

    # Baseline
    print("Running baseline model...")
    try:
        baseline_raw, baseline_ms = run_baseline(feature)
    except Exception as e:
        print(f"[ERROR] Baseline failed: {e}")
        return

    # Agent
    print("Running SprintAgent...")
    try:
        agent_plan, agent_ms = run_agent(feature)
    except Exception as e:
        print(f"[ERROR] Agent failed: {e}")
        return

    # Evaluate
    from metrics.evaluator import evaluate, print_report

    try:
        baseline_score = evaluate({}, baseline_ms, baseline_raw)
        agent_score = evaluate(agent_plan, agent_ms, json.dumps(agent_plan))
    except Exception as e:
        print(f"[ERROR] Evaluation failed: {e}")
        return

    # -----------------------
    # Results
    # -----------------------
    print("\n📊 Benchmark Results\n")

    print("Baseline:")
    print(f"Latency: {baseline_ms} ms")
    print(f"Score: {baseline_score.total}")

    print("\nSprintAgent:")
    print(f"Latency: {agent_ms} ms")
    print(f"Score: {agent_score.total}")

    print("\n📈 Detailed Report (Agent):")
    print_report(agent_score)

    # Optional: save results
    try:
        with open("benchmark_results.json", "w") as f:
            json.dump({
                "baseline": {
                    "latency_ms": baseline_ms,
                    "raw": baseline_raw,
                    "score": baseline_score.total,
                },
                "agent": {
                    "latency_ms": agent_ms,
                    "plan": agent_plan,
                    "score": agent_score.total,
                }
            }, f, indent=2)

        print("\nSaved results to benchmark_results.json")
    except Exception as e:
        print(f"[WARN] Failed to save results: {e}")