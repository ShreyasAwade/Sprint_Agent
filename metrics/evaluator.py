import json
import ast
import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class ScoreReport:
    task_quality: int
    code_quality: int
    planning_accuracy: int
    response_speed: int
    json_reliability: int
    total: int
    breakdown: dict


def score_task_quality(plan: dict) -> int:
    score = 0
    tasks = plan.get("tasks", [])
    if not tasks:
        return 0

    FIBONACCI = {1, 2, 3, 5, 8, 13}
    task_ids = {t.get("id") for t in tasks}
    required_fields = {"id", "title", "description", "story_points", "type", "acceptance_criteria"}

    complete = sum(1 for t in tasks if required_fields.issubset(t.keys()))
    score += min(800, int((complete / len(tasks)) * 800))

    if all(t.get("story_points") in FIBONACCI for t in tasks):
        score += 200

    if all(t.get("story_points", 99) <= 13 for t in tasks):
        score += 300

    dep_valid = all(
        all(d in task_ids for d in t.get("depends_on", []))
        for t in tasks
    )
    if dep_valid:
        score += 400

    avg_desc = sum(len(t.get("description", "")) for t in tasks) / len(tasks)
    if avg_desc < 200:
        score += 300

    types = {t.get("type") for t in tasks}
    if {"backend", "frontend", "test"}.issubset(types):
        score += 500

    unknowns = plan.get("unknowns", [])
    if unknowns and len(unknowns) >= 2:
        score += 500

    return min(3000, score)


def score_code_quality(plan: dict) -> int:
    score = 0
    tasks = plan.get("tasks", [])
    if not tasks:
        return 0

    stubs = [t.get("code_stub", "") for t in tasks]
    non_empty = [s for s in stubs if s and len(s) > 20]

    score += int((len(non_empty) / len(tasks)) * 500)

    valid_syntax = 0
    for stub in non_empty:
        try:
            ast.parse(stub)
            valid_syntax += 1
        except SyntaxError:
            pass
    if non_empty:
        score += int((valid_syntax / len(non_empty)) * 700)

    typed = sum(1 for s in non_empty if "->" in s or ": " in s)
    if non_empty:
        score += int((typed / len(non_empty)) * 400)

    documented = sum(1 for s in non_empty if '"""' in s or "'''" in s)
    if non_empty:
        score += int((documented / len(non_empty)) * 400)

    todos = sum(1 for s in non_empty if "TODO" in s or "raise NotImplementedError" in s)
    if non_empty:
        score += int((todos / len(non_empty)) * 300)

    secret_pattern = re.compile(r'(api_key\s*=\s*["\'][^"\']+["\']|password\s*=\s*["\'][^"\']+["\'])', re.I)
    if not any(secret_pattern.search(s) for s in non_empty):
        score += 200

    return min(2500, score)


def score_planning_accuracy(plan: dict) -> int:
    score = 0
    tasks = plan.get("tasks", [])

    if plan.get("feature_summary") and len(plan["feature_summary"]) > 20:
        score += 500

    declared = plan.get("total_story_points", -1)
    actual = sum(t.get("story_points", 0) for t in tasks)
    if declared == actual and actual > 0:
        score += 600

    if len(plan.get("sprint_recommendation", "")) > 50:
        score += 400

    if len(tasks) >= 3:
        score += 300

    with_risks = sum(1 for t in tasks if t.get("risks"))
    if tasks and (with_risks / len(tasks)) >= 0.5:
        score += 200

    return min(2000, score)


def score_response_speed(latency_ms: int) -> int:
    if latency_ms < 2000:  return 1500
    if latency_ms < 4000:  return 1200
    if latency_ms < 6000:  return 900
    if latency_ms < 10000: return 600
    if latency_ms < 15000: return 300
    return 100


def score_json_reliability(raw_response: str) -> int:
    try:
        parsed = json.loads(raw_response)
        score = 600
        required = {"feature_summary", "total_story_points", "tasks", "sprint_recommendation", "unknowns"}
        score += int((len(required & parsed.keys()) / len(required)) * 400)
        return score
    except (json.JSONDecodeError, TypeError):
        return 0


def evaluate(plan: dict, latency_ms: int, raw_response: Optional[str] = None) -> ScoreReport:
    raw = raw_response or json.dumps(plan)
    tq = score_task_quality(plan)
    cq = score_code_quality(plan)
    pa = score_planning_accuracy(plan)
    rs = score_response_speed(latency_ms)
    jr = score_json_reliability(raw)
    total = tq + cq + pa + rs + jr

    return ScoreReport(
        task_quality=tq, code_quality=cq, planning_accuracy=pa,
        response_speed=rs, json_reliability=jr, total=total,
        breakdown={
            "task_quality":      {"score": tq,    "max": 3000},
            "code_quality":      {"score": cq,    "max": 2500},
            "planning_accuracy": {"score": pa,    "max": 2000},
            "response_speed":    {"score": rs,    "max": 1500},
            "json_reliability":  {"score": jr,    "max": 1000},
            "TOTAL":             {"score": total, "max": 10000},
        }
    )


def print_report(report: ScoreReport):
    print("\n" + "="*50)
    print("  SPRINT AGENT — SCORE REPORT")
    print("="*50)
    for dim, data in report.breakdown.items():
        pct = round(data["score"] / data["max"] * 100, 1)
        bar = "█" * int(pct / 2.5) + "░" * (40 - int(pct / 2.5))
        print(f"  {dim:<22} {data['score']:>5}/{data['max']}  {pct}%")
    print("="*50)
    print(f"  TOTAL: {report.total} / 10,000")
    print("="*50 + "\n")