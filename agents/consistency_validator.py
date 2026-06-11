"""Cross-agent consistency validation after pipeline run."""
from __future__ import annotations

from typing import Any, Dict, List

from agents.intelligence import agent_envelope
from models.learner_state import LearnerState


class ConsistencyValidator:
  def __init__(self):
    self.name = "Consistency Validator"

  def run(self, state: LearnerState, report: Dict[str, Any]) -> Dict[str, Any]:
    warnings: List[str] = []
    checks_passed = 0
    total_checks = 0

    weakest = state.weakest_subject
    weakness = report.get("weakness_analysis", {})
    plan = report.get("study_plan", {})
    risk = report.get("risk_assessment", {})
    resources = report.get("resources", {})
    career = report.get("career_readiness", {})

    reported_weakest = (weakness.get("weakest_subject") or {}).get("subject")
    total_checks += 1
    if reported_weakest == weakest:
      checks_passed += 1
    else:
      warnings.append(
        f"Weakness analyzer reported {reported_weakest} but canonical weakest is {weakest}"
      )

    most_at_risk = (risk.get("most_at_risk") or {}).get("subject")
    total_checks += 1
    if not weakest or most_at_risk == weakest:
      checks_passed += 1
    else:
      warnings.append(
        f"Risk agent flagged {most_at_risk} as highest risk but weakest subject is {weakest}"
      )

    if weakest and plan.get("daily_schedule"):
      week_hours: Dict[str, float] = {}
      for day in plan["daily_schedule"][:7]:
        for sub in day.get("subjects", []):
          week_hours[sub["name"]] = week_hours.get(sub["name"], 0) + sub.get("hours", 0)
      strongest = state.strongest_subject
      weak_hours = week_hours.get(weakest, 0)
      strong_hours = week_hours.get(strongest, 0) if strongest else 0
      total_checks += 1
      if weak_hours >= strong_hours or len(state.subjects) == 1:
        checks_passed += 1
      else:
        warnings.append(
          f"Study planner allocated {weak_hours}h to {weakest} vs {strong_hours}h to {strongest} in week 1"
        )

    weak_resource = next(
      (r for r in resources.get("subject_resources", []) if r.get("subject") == weakest),
      None,
    )
    total_checks += 1
    if weak_resource and weak_resource.get("weakness_level") in {"weak", "moderate"}:
      checks_passed += 1
    elif not weakest:
      checks_passed += 1
    else:
      warnings.append(f"Resource agent did not prioritize resources for weakest subject {weakest}")

    career_weakest = career.get("weakest_subject")
    total_checks += 1
    if career_weakest == weakest:
      checks_passed += 1
    else:
      warnings.append(
        f"Career agent weakest ({career_weakest}) differs from canonical weakest ({weakest})"
      )

    degree_used = bool(career.get("structured_personalization", {}).get("selected_degree")) or state.learner_level in {"school", "cbse"}
    total_checks += 1
    if degree_used or state.learner_level == "school":
      checks_passed += 1
    else:
      warnings.append("Career output does not reflect selected degree for university learner")

    consistency_score = round((checks_passed / total_checks) * 100, 1) if total_checks else 0
    explanation = (
      f"{checks_passed}/{total_checks} cross-agent checks aligned on weakest subject '{weakest}'."
      if not warnings
      else "; ".join(warnings)
    )

    result = {
      "consistency_score": consistency_score,
      "checks_passed": checks_passed,
      "total_checks": total_checks,
      "inconsistency_warnings": warnings,
      "explanation": explanation,
      "canonical_weakest_subject": weakest,
    }
    result.update(agent_envelope(
      explanation,
      [
        f"Canonical weakest subject: {weakest}",
        f"Weakness vs risk vs plan vs resources vs career cross-checked",
        f"Passed {checks_passed} of {total_checks} consistency checks",
      ],
      consistency_score / 100,
      self.name,
      ["Assume agents agree without verification"],
      "Consistency is measured against the shared LearnerState priority ranking.",
      evidence=["Report Schema Validation", "Subject Alignment Assertions"],
    ))
    return result
