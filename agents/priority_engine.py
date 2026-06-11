"""Global priority engine — ranks subjects for all agents."""
from __future__ import annotations

from typing import Dict, List, Optional

from agents.intelligence import (
  classify_subject,
  exam_proximity_score,
  subject_confidence,
)
from models.student import Subject


class PriorityEngine:
  """Rank subjects using score gap, confidence gap, exam urgency, and relative weakness."""

  def confidence_for(self, subject: Subject, overrides: Optional[Dict[str, float]] = None) -> float:
    if overrides and subject.name in overrides:
      return max(0.0, min(1.0, overrides[subject.name]))
    explicit = getattr(subject, "confidence", None)
    if explicit is not None:
      return max(0.0, min(1.0, float(explicit)))
    return subject_confidence(subject)

  def priority_score(
    self,
    subject: Subject,
    confidence: Optional[float] = None,
    peer_average: float = 60.0,
  ) -> float:
    pct = max(0.0, min(100.0, subject.percentage))
    conf = confidence if confidence is not None else self.confidence_for(subject)
    conf_pct = conf * 100
    days = max(subject.days_until_exam, 0)
    score_gap = 100 - pct
    confidence_gap = 100 - conf_pct
    urgency = exam_proximity_score(days)
    relative_weakness = max(0.0, peer_average - pct) * 0.5
    return round(score_gap + confidence_gap + urgency + relative_weakness, 2)

  def rank_subjects(
    self,
    subjects: List[Subject],
    confidence_overrides: Optional[Dict[str, float]] = None,
  ) -> List[Dict]:
    if not subjects:
      return []

    peer_average = sum(s.percentage for s in subjects) / len(subjects)
    rows: List[Dict] = []
    for subject in subjects:
      confidence = self.confidence_for(subject, confidence_overrides)
      classification = classify_subject(subject.percentage)
      priority = self.priority_score(subject, confidence, peer_average)
      rows.append({
        "subject": subject.name,
        "percentage": round(subject.percentage, 2),
        "score": subject.score,
        "total": subject.total_marks,
        "classification": classification,
        "weakness_level": classification,
        "confidence": round(confidence, 2),
        "days_until_exam": subject.days_until_exam,
        "priority_score": priority,
        "exam_date": subject.exam_date.isoformat(),
      })

    rows.sort(
      key=lambda row: (
        -row["priority_score"],
        row["percentage"],
        row["days_until_exam"],
        row["subject"],
      )
    )
    return rows

  def summarize(self, ranking: List[Dict]) -> Dict:
    if not ranking:
      return {
        "weakest_subject": None,
        "moderate_subjects": [],
        "strongest_subject": None,
        "ranked_subjects": [],
      }

    weak = [r["subject"] for r in ranking if r["classification"] == "weak"]
    moderate = [r["subject"] for r in ranking if r["classification"] == "moderate"]
    strong = [r["subject"] for r in ranking if r["classification"] == "strong"]
    return {
      "weakest_subject": ranking[0]["subject"],
      "moderate_subjects": moderate,
      "strongest_subject": ranking[-1]["subject"] if ranking else None,
      "ranked_subjects": [r["subject"] for r in ranking],
      "weak_subjects": weak,
      "strong_subjects": strong,
    }
