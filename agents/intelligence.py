from dataclasses import asdict
from typing import Any, Dict, List

from models.student import StudentInput, Subject


from agents.input_normalizer import FAILSAFE_MESSAGE, validate_student_input as _validate_student_input

FAILSAFE_MESSAGE = FAILSAFE_MESSAGE
SUBJECT_THRESHOLDS = {
    "weak_max": 60.0,
    "moderate_max": 75.0,
}


def classify_subject(percentage: float) -> str:
    if percentage < SUBJECT_THRESHOLDS["weak_max"]:
        return "weak"
    if percentage <= SUBJECT_THRESHOLDS["moderate_max"]:
        return "moderate"
    return "strong"


def classification_rank(classification: str) -> int:
    return {"weak": 1, "moderate": 2, "strong": 3}.get(classification.lower(), 4)


def confidence_from_signals(*signals: float) -> float:
    clean = [max(0.0, min(1.0, float(signal))) for signal in signals]
    if not clean:
        return 0.75
    return round(sum(clean) / len(clean), 2)


def agent_envelope(
    final_output: str,
    reasoning_trace: List[str],
    confidence: float,
    agent_name: str = "Agent",
    rejected_options: List[str] | None = None,
    why_this_decision: str | None = None,
    evidence: List[str] | None = None,
) -> Dict[str, Any]:
    return {
        "final_output": final_output,
        "reasoning_trace": reasoning_trace,
        "evidence": evidence or [],
        "confidence": max(0.0, min(1.0, round(confidence, 2))),
        "why_this_decision": why_this_decision or (reasoning_trace[-1] if reasoning_trace else final_output),
        "rejected_options": rejected_options or [],
        "generated_by": agent_name,
    }


def exam_proximity_score(days_until_exam: int) -> float:
    days = max(days_until_exam, 0)
    return round(max(0.0, 30.0 - min(days, 30.0)), 2)


def subject_confidence(subject: Subject) -> float:
    data_quality = min(max(subject.total_marks, 1), 100) / 100
    exam_signal = 1.0 if subject.days_until_exam >= 0 else 0.5
    return confidence_from_signals(0.9, data_quality, exam_signal)


def priority_score(subject: Subject, confidence: float | None = None) -> float:
    pct = max(0.0, min(100.0, subject.percentage))
    conf_pct = (confidence if confidence is not None else subject_confidence(subject)) * 100
    return round((100 - pct) + (100 - conf_pct) + exam_proximity_score(subject.days_until_exam), 2)


def subject_trace(subject: Subject, classification: str) -> List[str]:
    confidence = subject_confidence(subject)
    return [
        f"Detected {subject.name} score at {subject.percentage:.1f}%",
        f"Classified {subject.name} as {classification.upper()}",
        f"Exam proximity is {max(subject.days_until_exam, 0)} days",
        f"Priority score = (100 - {subject.percentage:.1f}) + (100 - {confidence * 100:.1f}) + {exam_proximity_score(subject.days_until_exam):.1f}",
    ]


def validate_student_input(student: StudentInput) -> Dict[str, Any]:
    from agents.input_normalizer import normalize_student_input
    return _validate_student_input(normalize_student_input(student))


def serializable_report(report: Any) -> Dict[str, Any]:
    try:
        return asdict(report)
    except TypeError:
        return dict(report)
