import os
import json
import time
import re
from typing import Optional, Dict, Any, List

from dotenv import load_dotenv
from groq import Groq

# Load environment variables
load_dotenv()

# Initialize Groq client
client = Groq(api_key=os.getenv("SPRINT_AGENT_API_KEY"))

# Model config
MODEL_NAME = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")


# -----------------------
# SAFE SYSTEM PROMPT (NO TRIPLE QUOTE CONFLICT)
# -----------------------
SYSTEM_PROMPT = """
You are a senior software architect generating STRICT JSON sprint plans.

Return ONLY valid JSON. No explanation.

STRICT RULES:

1. TASK DESIGN:
- Each task must represent ONE responsibility
- NEVER group CRUD operations
- Split APIs into Create, Read, Update, Delete

2. STORY POINTS:
- Fibonacci only: 1,2,3,5,8,13
- total_story_points MUST equal sum(tasks)

3. CODE STUBS:
- MUST be valid Python
- MUST include:
  - type hints
  - explanation comments (purpose, params, return)
  - TODO comments
  - basic logic structure (not just pass)

Example format:
def example_function(x: int) -> int:
    # Purpose: Calculate processed value
    # Args: x (int)
    # Returns: int
    # TODO: implement logic
    result = x * 2
    return result

4. RISKS:
- Must be specific technical failure scenarios
- Avoid generic terms like "performance issues"
- Example: race conditions, stale cache, DB transaction failures

5. ACCEPTANCE CRITERIA:
- Must be testable and measurable
- Include API behavior, outputs, status codes

6. SPRINT RECOMMENDATION:
- Must include:
  - execution order
  - parallel tasks
  - dependency blockers

7. UNKNOWNS:
- At least 2 real uncertainties

8. OUTPUT FORMAT (MANDATORY):

Each task MUST follow EXACTLY this schema:

{
  "id": "T-001",
  "title": "string",
  "description": "string",
  "story_points": number,
  "depends_on": [],
  "type": "backend|frontend|infra|test|docs",
  "code_stub": "string",
  "risks": ["string"],
  "acceptance_criteria": ["string"]
}

DO NOT change field names.

FINAL OUTPUT SCHEMA:
{
  "feature_summary": "string",
  "total_story_points": number,
  "tasks": [
    {
      "id": "T-001",
      "title": "string",
      "description": "string",
      "story_points": number,
      "depends_on": [],
      "type": "backend|frontend|infra|test|docs",
      "code_stub": "string",
      "risks": ["string"],
      "acceptance_criteria": ["string"]
    }
  ],
  "sprint_recommendation": "string",
  "unknowns": ["string", "string"]
}
"""


# -----------------------
# Sprint Agent
# -----------------------
class SprintAgent:
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.session_metadata = {
            "start_time": time.time(),
            "requests": 0,
            "tasks_generated": 0,
        }

    def _log(self, msg: str):
        if self.verbose:
            print(f"[SprintAgent] {msg}")

    def _call_llm(self, messages):
        return client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            temperature=0.1  # deterministic output
        )

    # -----------------------
    # MAIN FUNCTION
    # -----------------------
    def plan(self, feature_request: str, context: Optional[str] = None) -> Dict[str, Any]:
        self._log(f"Planning: {feature_request[:80]}...")

        user_prompt = f"""
Generate STRICT JSON ONLY.

Feature:
{feature_request}
"""

        response = self._call_llm([
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ])

        raw_output = response.choices[0].message.content
        parsed = self._safe_json_parse(raw_output)

        # Retry if JSON invalid OR schema mismatch
        if parsed.get("parse_error") or not self._validate_schema(parsed):
            self._log("Retrying due to invalid JSON or schema mismatch...")
            parsed = self._retry_fix(raw_output)

        parsed = self._fix_story_points(parsed)

        self.session_metadata["tasks_generated"] += len(parsed.get("tasks", []))
        return parsed

    # -----------------------
    # RETRY FIX
    # -----------------------
    def _retry_fix(self, bad_output: str) -> Dict[str, Any]:
        repair_prompt = f"""
Fix this into STRICT VALID JSON following EXACT schema.
Do not change field names.
Return ONLY JSON.

{bad_output}
"""

        response = self._call_llm([
            {"role": "system", "content": "You strictly fix JSON and enforce schema."},
            {"role": "user", "content": repair_prompt}
        ])

        return self._safe_json_parse(response.choices[0].message.content)

    # -----------------------
    # JSON PARSER
    # -----------------------
    def _safe_json_parse(self, raw: str) -> Dict[str, Any]:
        try:
            return json.loads(raw)
        except:
            match = re.search(r"\{.*\}", raw, re.DOTALL)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            return {"parse_error": True, "raw": raw}

    # -----------------------
    # SCHEMA VALIDATION
    # -----------------------
    def _validate_schema(self, plan: Dict[str, Any]) -> bool:
        if "tasks" not in plan:
            return False

        required_fields = {
            "id", "title", "description",
            "story_points", "depends_on",
            "type", "code_stub",
            "risks", "acceptance_criteria"
        }

        for task in plan.get("tasks", []):
            if not isinstance(task, dict):
                return False
            if not required_fields.issubset(task.keys()):
                return False

        return True

    # -----------------------
    # FIX STORY POINTS
    # -----------------------
    def _fix_story_points(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        tasks = plan.get("tasks", [])
        total = sum(t.get("story_points", 0) for t in tasks)
        plan["total_story_points"] = total
        return plan

    # -----------------------
    # REFINE
    # -----------------------
    def refine(self, feedback: str) -> Dict[str, Any]:
        return self.plan(feedback)

    # -----------------------
    # STATS
    # -----------------------
    def get_session_stats(self) -> Dict[str, Any]:
        self.session_metadata["duration"] = round(
            time.time() - self.session_metadata["start_time"], 2
        )
        return self.session_metadata