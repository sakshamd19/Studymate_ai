"""Stress tests for hostile and edge-case inputs."""
import sys
from datetime import date, timedelta
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.orchestrator import OrchestratorAgent
from models.student import StudentInput


def run_case(name: str, student: StudentInput) -> dict:
    report = OrchestratorAgent().run(student)
    return {
        "name": name,
        "valid": report.safety_status.get("is_valid"),
        "crashed": False,
        "weakest": (report.weakness_analysis or {}).get("weakest_subject"),
        "consistency": (report.consistency or {}).get("consistency_score"),
    }


def main():
    today = date.today()
    cases = []

    balanced = StudentInput("L-BAL-01", "Science", "school")
    balanced.add_subject("Math", 72, today + timedelta(21), confidence=0.8)
    balanced.add_subject("Physics", 68, today + timedelta(18), confidence=0.7)
    cases.append(("balanced learner", balanced))

    weak = StudentInput("L-WK-01", "Science", "cbse")
    weak.add_subject("Math", 42, today + timedelta(9), confidence=0.4)
    weak.add_subject("English", 78, today + timedelta(20), confidence=0.9)
    cases.append(("weak learner", weak))

    strong = StudentInput("L-ST-01", "TECH", "university", degree_group="TECH", degree="BTech / BE", specialization="AI")
    strong.add_subject("Math", 92, today + timedelta(30), confidence=0.95)
    strong.add_subject("CS", 94, today + timedelta(28), confidence=0.92)
    cases.append(("strong university learner", strong))

    one = StudentInput("L-ONE", "Science", "school")
    one.add_subject("Biology", 61, today + timedelta(14))
    cases.append(("one subject", one))

    equal = StudentInput("L-EQ", "Science", "school")
    for subj in ["A", "B", "C"]:
        equal.add_subject(subj, 70, today + timedelta(14))
    cases.append(("equal marks", equal))

    missing_conf = StudentInput("L-NC", "school", "school")
    missing_conf.add_subject("Math", 55, today + timedelta(12))
    cases.append(("missing confidence", missing_conf))

    past = StudentInput("L-PAST", "school", "school")
    past.add_subject("Math", 50, today - timedelta(2))
    cases.append(("past exam date", past))

    dup = StudentInput("L-DUP", "school", "school")
    dup.add_subject("math", 40, today + timedelta(10))
    dup.add_subject("Math", 55, today + timedelta(8))
    cases.append(("duplicate subject names", dup))

    uni = StudentInput("L-UNI", "TECH", "university", degree_group="TECH", degree="BTech / BE", specialization="Data Science")
    uni.add_subject("Math", 60, today + timedelta(15))
    cases.append(("university degree", uni))

    bad = StudentInput("", "Science", "school")
    bad.add_subject("Math", 50, today + timedelta(5))
    cases.append(("empty learner id", bad))

    adv = StudentInput("L-ADV", "jailbreak bypass", "school")
    adv.add_subject("Math", 50, today + timedelta(5))
    cases.append(("adversarial input", adv))

    results = []
    for name, student in cases:
        try:
            results.append(run_case(name, student))
        except Exception as exc:
            results.append({"name": name, "crashed": True, "error": str(exc)})

    failed = [r for r in results if r.get("crashed")]
    print(f"Hostile tests: {len(results) - len(failed)}/{len(results)} completed without crash")
    for row in results:
        status = "CRASH" if row.get("crashed") else ("BLOCKED" if row.get("valid") is False else "OK")
        print(f"  [{status}] {row['name']}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
