"""Input normalization and validation — safe but not hostile."""
from __future__ import annotations

import re
from datetime import date
from typing import Dict, List, Tuple

from models.student import StudentInput, Subject

FAILSAFE_MESSAGE = "I cannot generate a reliable plan. Please provide more details."

DEGREE_ALIASES = {
  "btech": "BTech",
  "b.tech": "BTech",
  "b tech": "BTech",
  "be": "BTech / BE",
  "b.e.": "BTech / BE",
  "bca": "BCA",
  "bsc cs": "BSc Computer Science",
  "bba": "BBA",
  "bcom": "BCom",
  "llb": "LLB",
  "mbbs": "MBBS",
}

SPECIALIZATION_ALIASES = {
  "ai": "Artificial Intelligence",
  "artificial intelligence": "Artificial Intelligence",
  "ml": "Data Science",
  "data science": "Data Science",
  "cyber security": "Cybersecurity",
  "cybersecurity": "Cybersecurity",
  "software engineering": "Software Engineering",
  "software dev": "Software Development",
}

SUBJECT_ALIASES = {
  "math": "Mathematics",
  "maths": "Mathematics",
  "mathematics": "Mathematics",
  "phy": "Physics",
  "physics": "Physics",
  "chem": "Chemistry",
  "chemistry": "Chemistry",
  "bio": "Biology",
  "biology": "Biology",
  "cs": "Computer Science",
  "computer science": "Computer Science",
  "comp sci": "Computer Science",
  "eng": "English",
  "english": "English",
  "eco": "Economics",
  "economics": "Economics",
  "hist": "History",
  "history": "History",
}

LEVEL_ALIASES = {
  "school": "school",
  "cbse": "cbse",
  "board": "cbse",
  "university": "university",
  "college": "university",
  "ug": "university",
  "advanced": "advanced",
  "professional": "advanced",
  "pro": "advanced",
}


def _title_case_phrase(value: str) -> str:
  return " ".join(part.capitalize() for part in value.split())


def normalize_whitespace(value: str) -> str:
  return re.sub(r"\s+", " ", (value or "").strip())


def normalize_learner_level(value: str) -> str:
  key = normalize_whitespace(value).lower()
  return LEVEL_ALIASES.get(key, key if key in LEVEL_ALIASES.values() else "school")


def normalize_degree(value: str) -> str:
  key = normalize_whitespace(value).lower()
  if not key:
    return ""
  if key in DEGREE_ALIASES:
    return DEGREE_ALIASES[key]
  return _title_case_phrase(key)


def normalize_specialization(value: str) -> str:
  key = normalize_whitespace(value).lower()
  if not key:
    return ""
  if key in SPECIALIZATION_ALIASES:
    return SPECIALIZATION_ALIASES[key]
  return _title_case_phrase(key)


def normalize_subject_name(value: str) -> str:
  key = normalize_whitespace(value).lower()
  if not key:
    return ""
  if key in SUBJECT_ALIASES:
    return SUBJECT_ALIASES[key]
  return _title_case_phrase(key)


def normalize_learner_id(value: str) -> str:
  return normalize_whitespace(value)


def dedupe_subjects(subjects: List[Subject]) -> List[Subject]:
  seen: Dict[str, Subject] = {}
  for subject in subjects:
    key = normalize_subject_name(subject.name).lower()
    if not key:
      continue
    if key in seen:
      existing = seen[key]
      existing.score = max(existing.score, subject.score)
      if subject.exam_date < existing.exam_date:
        existing.exam_date = subject.exam_date
    else:
      seen[key] = Subject(
        name=normalize_subject_name(subject.name),
        score=max(0.0, subject.score),
        exam_date=subject.exam_date,
        total_marks=subject.total_marks,
        confidence=getattr(subject, "confidence", None),
      )
  return list(seen.values())


def normalize_student_input(student: StudentInput) -> StudentInput:
  student.name = normalize_learner_id(student.name)
  student.stream = normalize_whitespace(student.stream)
  student.learner_level = normalize_learner_level(student.learner_level)
  student.degree_group = normalize_whitespace(student.degree_group).upper()
  student.degree = normalize_degree(student.degree)
  student.specialization = normalize_specialization(student.specialization)
  student.interest = normalize_specialization(student.interest) if student.interest else ""
  normalized_subjects = []
  for subject in dedupe_subjects(student.subjects):
    subject.score = max(0.0, min(subject.score, subject.total_marks))
    normalized_subjects.append(subject)
  student.subjects = normalized_subjects
  return student


def validate_student_input(student: StudentInput) -> Dict:
  issues: List[str] = []
  text_fields = [
    student.name,
    student.stream,
    student.learner_level,
    student.degree_group,
    student.degree,
    student.specialization,
    student.interest,
  ]
  text_fields.extend(subject.name for subject in student.subjects)
  joined = " ".join(str(field).lower() for field in text_fields)

  adversarial_terms = [
    "ignore previous",
    "system prompt",
    "developer message",
    "jailbreak",
    "reveal secrets",
    "bypass",
  ]
  if any(term in joined for term in adversarial_terms):
    issues.append("Adversarial instruction detected in learner input")

  pii_markers = ["@", "phone", "aadhaar", "ssn", "passport"]
  email_pattern = re.compile(r"\b[\w.+-]+@[\w.-]+\.\w+\b")
  if email_pattern.search(joined) or any(marker in joined for marker in pii_markers):
    issues.append("Possible PII detected; only synthetic learner data is allowed")

  learner_id = student.name.strip() if student.name else ""
  if not learner_id:
    issues.append("Missing learner ID")
  elif len(learner_id) < 2:
    issues.append("Learner ID is too short")

  if student.learner_level not in {"school", "cbse", "university", "advanced"}:
    issues.append(f"Invalid learner level: {student.learner_level}")

  if student.learner_level in {"university", "advanced"} and not student.degree:
    issues.append("Degree is required for university/advanced learners")

  if not student.subjects:
    issues.append("No subjects supplied")

  names_seen = set()
  for subject in student.subjects:
    norm_name = normalize_subject_name(subject.name)
    if not norm_name:
      issues.append("Subject name is required")
      continue
    if norm_name.lower() in names_seen:
      issues.append(f"Duplicate subject after normalization: {norm_name}")
    names_seen.add(norm_name.lower())
    if subject.score is None or subject.total_marks <= 0:
      issues.append(f"Score and total marks are required for {norm_name}")
    if subject.score > subject.total_marks:
      issues.append(f"Invalid score for {norm_name}: exceeds total marks")

  warnings = [
    f"Exam date for {normalize_subject_name(s.name)} is in the past — treating as immediate urgency"
    for s in student.subjects
    if s.exam_date < date.today()
  ]

  return {
    "is_valid": not issues,
    "issues": issues,
    "warnings": warnings,
    "message": FAILSAFE_MESSAGE if issues else "Input passed synthetic-data and sufficiency checks.",
  }


def build_skill_profile(student: StudentInput) -> Dict[str, float]:
  profile: Dict[str, float] = {}
  for subject in student.subjects:
    name = normalize_subject_name(subject.name)
    conf = getattr(subject, "confidence", None)
    if conf is None:
      conf = 0.75 + (0.2 if subject.percentage >= 70 else 0.0)
    profile[name] = round(max(0.1, min(1.0, float(conf))), 2)

  spec = normalize_specialization(student.specialization).lower()
  if spec:
    profile[f"specialization:{spec}"] = 0.6 if student.learner_level in {"university", "advanced"} else 0.4
  interest = normalize_specialization(student.interest).lower()
  if interest:
    profile[f"interest:{interest}"] = 0.55
  return profile
