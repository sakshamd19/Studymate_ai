from dataclasses import dataclass, field
from typing import Dict, List
from datetime import date

@dataclass
class Subject:
    name: str
    score: float
    exam_date: date
    total_marks: float = 100.0
    confidence: float | None = None

    @property
    def percentage(self) -> float:
        return (self.score / self.total_marks) * 100

    @property
    def days_until_exam(self) -> int:
        return (self.exam_date - date.today()).days

@dataclass
class StudentInput:
    name: str
    stream: str
    learner_level: str = "school"
    degree_group: str = ""
    degree: str = ""
    specialization: str = ""
    interest: str = ""
    subjects: List[Subject] = field(default_factory=list)

    def add_subject(
        self,
        name: str,
        score: float,
        exam_date: date,
        total_marks: float = 100.0,
        confidence: float | None = None,
    ):
        self.subjects.append(Subject(name, score, exam_date, total_marks, confidence))

    def get_weak_subjects(self, threshold: float = 60.0) -> List[Subject]:
        return [s for s in self.subjects if s.percentage < threshold]

    def get_subject_by_name(self, name: str) -> Subject:
        return next((s for s in self.subjects if s.name == name), None)

@dataclass
class AgentReport:
    learning_path: dict = field(default_factory=dict)
    engagement_tracking: dict = field(default_factory=dict)
    assessment: dict = field(default_factory=dict)
    manager_insights: dict = field(default_factory=dict)
    weakness_analysis: dict = field(default_factory=dict)
    study_plan: dict = field(default_factory=dict)
    risk_assessment: dict = field(default_factory=dict)
    resources: dict = field(default_factory=dict)
    career_readiness: dict = field(default_factory=dict)
    peer_benchmarking: dict = field(default_factory=dict)
    learner_state: dict = field(default_factory=dict)
    consistency: dict = field(default_factory=dict)
    consensus: dict = field(default_factory=dict)
    counterfactuals: dict = field(default_factory=dict)
    critic_review: dict = field(default_factory=dict)
    evaluation: dict = field(default_factory=dict)
    observability: dict = field(default_factory=dict)
    safety_status: dict = field(default_factory=dict)
    foundry_iq: dict = field(default_factory=dict)
