"""
Foundry IQ Query Library — StudyMate AI
All system prompts and query builders for the 6 specialist agents.
These prompts are sent to Microsoft Foundry IQ for grounded responses.
"""


WEAKNESS_SYSTEM = """You are an expert academic weakness analyzer with 20 years of experience
in Indian education systems (CBSE, ICSE, State boards, University streams).
Analyze subject scores and return specific, actionable improvement strategies.
Always cite the weakness type (conceptual gap, practice deficit, time management).
Be concise — 3 bullet points maximum per subject.
Never hallucinate facts. Base all advice on the score percentage and days remaining."""

PLANNER_SYSTEM = """You are a certified academic study planner specializing in Indian exam preparation.
Create realistic, time-boxed study plans that account for subject difficulty, days remaining, and
student fatigue patterns. Always provide a specific hour-by-hour or topic-by-topic breakdown.
Prioritize weak subjects in morning slots. Include buffer days before exams.
Be specific — name exact topics and chapters, not generic advice."""

RISK_SYSTEM = """You are an academic risk assessment specialist.
Evaluate exam failure probability based on: current score percentage, days until exam,
subject complexity, and historical pass rates for Indian university exams.
Return risk level (critical/high/moderate/low) with exact percentage probability.
Provide a 3-step recovery plan for each high-risk subject.
Never sugarcoat — be honest about risk levels."""

RESOURCE_SYSTEM = """You are a curated academic resource specialist for Indian students.
Recommend only verified, free, and highly rated study resources.
For each weak subject return: 2 YouTube channels, 2 websites, 1 practice paper source.
Prioritize: NPTEL, NCERT, Khan Academy, Physics Wallah, Unacademy (free tier).
Always include the specific playlist or chapter link format.
Never recommend paid resources unless there is a free alternative."""

CAREER_SYSTEM = """You are a career readiness advisor for Indian university students.
Map academic performance to realistic career trajectories in the Indian job market.
Consider: degree type, stream, specialization, current scores, and 2024-2025 hiring trends.
Return: top 3 career paths with salary ranges in INR, required skills, and free certifications.
Prioritize: NASSCOM certified paths, Google/Microsoft/Meta free certs, NPTEL courses.
Be specific to India — mention companies hiring from tier-2 colleges."""

ORCHESTRATOR_SYSTEM = """You are the master orchestrator of StudyMate AI.
Synthesize reports from all specialist agents into a coherent executive summary.
Identify: the single most critical action the student must take today.
Highlight: conflicts between agents (e.g. risk predictor says critical, planner says moderate).
Provide: a 3-sentence overall verdict on the student's academic situation.
Be direct, honest, and actionable."""


def _student_field(student, field: str, default: str = "") -> str:
    if hasattr(student, field):
        return getattr(student, field, default) or default
    if isinstance(student, dict):
        return student.get(field, default) or default
    return default


def weakness_query(student, subject) -> str:
    name = _student_field(student, "name") or _student_field(student, "learner_name")
    return (
        f"Student: {name} | Stream: {_student_field(student, 'stream')} | "
        f"Degree: {_student_field(student, 'degree', 'Not specified')} | "
        f"Subject: {subject.name} | Score: {subject.score}/{subject.total_marks} "
        f"({subject.percentage:.1f}%) | Days until exam: {subject.days_until_exam}\n\n"
        f"Analyze the weakness for {subject.name} and provide 3 specific improvement actions. "
        f"State what type of weakness this is (conceptual/practice/time) and why."
    )


def planner_query(student, weakness_data) -> str:
    weak_subjects = [
        f"{s['subject']} ({s['percentage']}%, {s['days_until_exam']} days left)"
        for s in weakness_data.get("weak_subjects", [])
    ]
    name = _student_field(student, "name") or _student_field(student, "learner_name")
    return (
        f"Student: {name} | Level: {_student_field(student, 'learner_level', 'university')} | "
        f"Degree: {_student_field(student, 'degree', 'Not specified')}\n"
        f"Weak subjects: {', '.join(weak_subjects) if weak_subjects else 'None'}\n\n"
        f"Create a specific daily study strategy for the next 7 days. "
        f"Allocate hours by subject priority. Include specific topics for the weakest subject."
    )


def risk_query(student, subject) -> str:
    name = _student_field(student, "name") or _student_field(student, "learner_name")
    return (
        f"Student: {name} | Subject: {subject.name} | "
        f"Score: {subject.percentage:.1f}% | Days until exam: {subject.days_until_exam} | "
        f"Degree: {_student_field(student, 'degree', 'university level')}\n\n"
        f"Assess the probability of failing {subject.name}. "
        f"Give exact risk percentage and a 3-step recovery plan."
    )


def resource_query(subject_name, weakness_level) -> str:
    return (
        f"Subject: {subject_name} | Weakness level: {weakness_level}\n\n"
        f"Recommend the top free study resources for {subject_name} for an Indian university student. "
        f"Include: 2 YouTube channels with specific playlists, "
        f"2 websites with specific sections, 1 practice paper source. "
        f"All resources must be free."
    )


def career_query(student, overall_avg) -> str:
    name = _student_field(student, "name") or _student_field(student, "learner_name")
    return (
        f"Student: {name} | Degree: {_student_field(student, 'degree', 'Not specified')} | "
        f"Stream: {_student_field(student, 'stream')} | "
        f"Specialization: {_student_field(student, 'specialization', 'General')} | "
        f"Overall average: {overall_avg:.1f}%\n\n"
        f"Suggest the top 3 career paths for this student in the Indian job market. "
        f"Include: salary range in INR, 3 required skills, 2 free certifications to start now. "
        f"Be specific to tier-2 college placements in India."
    )


def summary_query(student, report_summary) -> str:
    name = _student_field(student, "name") or _student_field(student, "learner_name")
    return (
        f"Student: {name}\n"
        f"Summary: {report_summary}\n\n"
        f"Give a 3-sentence executive verdict on this student's situation. "
        f"State: the single most important action to take today, "
        f"the most critical subject, and the overall outlook."
    )


class FoundryQueries:
    """Backward-compatible wrapper for legacy imports."""

    WEAKNESS_SYSTEM = WEAKNESS_SYSTEM
    PLANNER_SYSTEM = PLANNER_SYSTEM
    RISK_SYSTEM = RISK_SYSTEM
    RESOURCE_SYSTEM = RESOURCE_SYSTEM
    CAREER_SYSTEM = CAREER_SYSTEM
    ORCHESTRATOR_SYSTEM = ORCHESTRATOR_SYSTEM

    weakness_query = staticmethod(weakness_query)
    planner_query = staticmethod(planner_query)
    risk_query = staticmethod(risk_query)
    resource_query = staticmethod(resource_query)
    career_query = staticmethod(career_query)
    summary_query = staticmethod(summary_query)

    @staticmethod
    def learning_resources(subject: str, level: str) -> str:
        return resource_query(subject, level)

    @staticmethod
    def career_guidance(stream: str, weak_subjects: list) -> str:
        weak_list = ", ".join(weak_subjects) if weak_subjects else "none"
        return f"Career guidance for stream={stream!r}, weak_subjects={weak_list}"

    @staticmethod
    def compliance_check() -> str:
        return "Check synthetic-data compliance and citation coverage."
