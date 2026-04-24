from dataclasses import dataclass
import json


@dataclass
class ScoreReport:
    task_quality: int
    code_quality: int
    planning_accuracy: int
    response_speed: int
    json_reliability: int

    @property
    def total(self):
        return (
            self.task_quality
            + self.code_quality
            + self.planning_accuracy
            + self.response_speed
            + self.json_reliability
        )


def score_task_quality(plan: dict) -> int:
    tasks = plan.get("tasks", [])
    if not tasks:
        return 0

    score = 0

    if len(tasks) >= 5:
        score += 2000

    for t in tasks:
        if t.get("title") and t.get("description"):
            score += 100

    return min(score, 3000)


def score_code_quality(plan: dict) -> int:
    score = 0

    for t in plan.get("tasks", []):
        code = t.get("code_stub", "")

        if "def " in code:
            score += 200
        if "->" in code:
            score += 200
        if '"""' in code:
            score += 300
        if "TODO" in code:
            score += 100

    return min(score, 2500)


def score_planning_accuracy(plan: dict) -> int:
    tasks = plan.get("tasks", [])
    total = plan.get("total_story_points", 0)
    calc = sum(t.get("story_points", 0) for t in tasks)

    if total == calc:
        return 2000
    return 500


def score_response_speed(ms: int) -> int:
    if ms < 2000:
        return 1500
    elif ms < 5000:
        return 900
    return 300


def score_json_reliability(raw: str) -> int:
    try:
        json.loads(raw)
        return 1000
    except:
        return 300


def evaluate(plan: dict, latency_ms: int, raw: str) -> ScoreReport:
    return ScoreReport(
        task_quality=score_task_quality(plan),
        code_quality=score_code_quality(plan),
        planning_accuracy=score_planning_accuracy(plan),
        response_speed=score_response_speed(latency_ms),
        json_reliability=score_json_reliability(raw),
    )