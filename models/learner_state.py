"""Canonical learner state — single source of truth for all agents."""
from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Any, Dict, List, Optional

from models.student import StudentInput, Subject


@dataclass
class LearnerState:
  learner_id: str
  learner_name: str
  learner_level: str
  degree_group: str
  degree: str
  specialization: str
  skill_profile: Dict[str, float]
  stream: str
  interest: str
  subjects: List[Subject]
  subject_scores: Dict[str, float] = field(default_factory=dict)
  subject_confidence: Dict[str, float] = field(default_factory=dict)
  exam_dates: Dict[str, date] = field(default_factory=dict)
  days_remaining: Dict[str, int] = field(default_factory=dict)
  ranked_subjects: List[str] = field(default_factory=list)
  weakest_subject: Optional[str] = None
  moderate_subjects: List[str] = field(default_factory=list)
  strongest_subject: Optional[str] = None
  study_capacity: float = 6.0
  risk_profile: Dict[str, float] = field(default_factory=dict)
  confidence_profile: Dict[str, float] = field(default_factory=dict)
  language: str = "en"
  prior_state: Optional[Dict[str, Any]] = None
  priority_ranking: List[Dict[str, Any]] = field(default_factory=list)
  test_mode: bool = False

  def get_subject(self, name: str) -> Optional[Subject]:
    key = name.strip().lower()
    for subject in self.subjects:
      if subject.name.strip().lower() == key:
        return subject
    return None

  def classification_for(self, name: str) -> str:
    for row in self.priority_ranking:
      if row.get("subject") == name:
        return row.get("classification", "moderate")
    return "moderate"

  @classmethod
  def from_student(
    cls,
    student: StudentInput,
    *,
    study_capacity: float = 6.0,
    language: str = "en",
    prior_state: Optional[Dict[str, Any]] = None,
    test_mode: bool = False,
  ) -> "LearnerState":
    from agents.input_normalizer import build_skill_profile, normalize_student_input
    from agents.priority_engine import PriorityEngine
    from agents.risk_predictor import RiskPredictorAgent

    student = normalize_student_input(student)
    engine = PriorityEngine()
    ranking = engine.rank_subjects(student.subjects)
    summary = engine.summarize(ranking)
    risk_agent = RiskPredictorAgent()

    subject_scores = {s.name: round(s.percentage, 2) for s in student.subjects}
    subject_confidence = {s.name: engine.confidence_for(s) for s in student.subjects}
    exam_dates = {s.name: s.exam_date for s in student.subjects}
    days_remaining = {s.name: max(s.days_until_exam, 0) for s in student.subjects}
    risk_profile = {
      s.name: risk_agent.calculate_risk_score(s)
      for s in student.subjects
      if s.days_until_exam >= 0
    }

    return cls(
      learner_id=student.name,
      learner_name=student.name,
      learner_level=student.learner_level,
      degree_group=student.degree_group,
      degree=student.degree,
      specialization=student.specialization,
      skill_profile=build_skill_profile(student),
      stream=student.stream,
      interest=student.interest,
      subjects=student.subjects,
      subject_scores=subject_scores,
      subject_confidence=subject_confidence,
      exam_dates=exam_dates,
      days_remaining=days_remaining,
      ranked_subjects=summary["ranked_subjects"],
      weakest_subject=summary["weakest_subject"],
      moderate_subjects=summary["moderate_subjects"],
      strongest_subject=summary["strongest_subject"],
      study_capacity=study_capacity,
      risk_profile=risk_profile,
      confidence_profile=subject_confidence,
      language=language,
      prior_state=prior_state,
      priority_ranking=ranking,
      test_mode=test_mode,
    )

  def to_student_input(self) -> StudentInput:
    student = StudentInput(
      name=self.learner_id,
      stream=self.stream,
      learner_level=self.learner_level,
      degree_group=self.degree_group,
      degree=self.degree,
      specialization=self.specialization,
      interest=self.interest,
    )
    for subject in self.subjects:
      student.add_subject(subject.name, subject.score, subject.exam_date, subject.total_marks)
    return student
