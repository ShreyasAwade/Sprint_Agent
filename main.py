import argparse
import json
import sys
import time
import os
from typing import Optional

from dotenv import load_dotenv

# Load env variables
load_dotenv()

from agent.core import SprintAgent
from metrics.evaluator import evaluate, print_report


DEMO_REQUEST = """
Build a real-time collaborative document editor.
- Multiple users edit simultaneously (WebSockets)
- Full revision history
- Role-based access: owner, editor, viewer
Stack: FastAPI, React, PostgreSQL, Redis
"""


# -----------------------
# Helpers
# -----------------------

def check_api_key(required: bool = True) -> bool:
    key_exists = bool(os.environ.get("SPRINT_AGENT_API_KEY"))

    if required and not key_exists:
        print("ERROR: SPRINT_AGENT_API_KEY not set.")
        print("→ Copy .env.example to .env and add your Groq API key.")
        return False

    return key_exists


def safe_plan(agent: SprintAgent, prompt: str, refine: bool = False):
    try:
        start = time.time()

        plan = agent.refine(prompt) if refine else agent.plan(prompt)

        latency_ms = int((time.time() - start) * 1000)

        if not isinstance(plan, dict):
            raise ValueError("Invalid plan format")

        return plan, latency_ms

    except Exception as e:
        print(f"[ERROR] Agent failed: {str(e)}")
        return None, None


# -----------------------
# Demo Mode
# -----------------------

def run_demo():
    if not check_api_key():
        return

    agent = SprintAgent()

    plan, latency_ms = safe_plan(agent, DEMO_REQUEST)

    if not plan:
        print("Demo failed.")
        return

    print(json.dumps(plan, indent=2))

    try:
        report = evaluate(plan, latency_ms, json.dumps(plan))
        print_report(report)
    except Exception as e:
        print(f"[WARN] Evaluation failed: {e}")

    try:
        with open("demo_output.json", "w") as f:
            json.dump(plan, f, indent=2)
        print("Saved to demo_output.json")
    except Exception as e:
        print(f"[WARN] Failed to save file: {e}")


# -----------------------
# Interactive Mode
# -----------------------

def run_interactive():
    if not check_api_key():
        return

    agent = SprintAgent()

    print("\nSprint Agent CLI")
    print("Type 'quit' to exit | 'stats' for session info | 'score' to evaluate last plan\n")

    last_plan: Optional[dict] = None
    last_latency: Optional[int] = None

    while True:
        try:
            feature = input("Feature > ").strip()

            if not feature:
                continue

            if feature.lower() == "quit":
                print("Exiting...")
                break

            if feature.lower() == "stats":
                print(json.dumps(agent.get_session_stats(), indent=2))
                continue

            if feature.lower() == "score":
                if not last_plan:
                    print("No plan available to score.")
                    continue

                try:
                    report = evaluate(last_plan, last_latency, json.dumps(last_plan))
                    print_report(report)
                except Exception as e:
                    print(f"[WARN] Evaluation failed: {e}")
                continue

            # Run agent
            plan, latency = safe_plan(agent, feature, refine=bool(last_plan))

            if not plan:
                continue

            last_plan = plan
            last_latency = latency

            print(json.dumps(plan, indent=2))

        except KeyboardInterrupt:
            print("\nInterrupted. Type 'quit' to exit.")
        except Exception as e:
            print(f"[ERROR] Unexpected issue: {e}")


# -----------------------
# Benchmark Mode
# -----------------------

def run_benchmark():
    if not check_api_key():
        return

    try:
        from benchmarks.compare import run_benchmark
    except ImportError:
        print("Benchmark module not found.")
        return

    run_benchmark(DEMO_REQUEST.strip())


# -----------------------
# Score Existing File
# -----------------------

def run_score(file_path: str):
    try:
        with open(file_path) as f:
            plan = json.load(f)

        report = evaluate(plan, 5000, json.dumps(plan))
        print_report(report)

    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except json.JSONDecodeError:
        print("Invalid JSON file.")
    except Exception as e:
        print(f"[ERROR] Failed to score: {e}")


# -----------------------
# Main CLI Entry
# -----------------------

def main():
    parser = argparse.ArgumentParser(description="Sprint Agent CLI")

    parser.add_argument("--benchmark", action="store_true", help="Run benchmark")
    parser.add_argument("--demo", action="store_true", help="Run demo")
    parser.add_argument("--score", metavar="FILE", help="Score an existing JSON plan")

    args = parser.parse_args()

    if args.benchmark:
        run_benchmark()
    elif args.demo:
        run_demo()
    elif args.score:
        run_score(args.score)
    else:
        run_interactive()


if __name__ == "__main__":
    main()