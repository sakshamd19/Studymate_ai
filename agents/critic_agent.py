from typing import Dict, List

from agents.intelligence import agent_envelope
from models.learner_state import LearnerState


class CriticAgent:
    def __init__(self):
        self.name = "Critic Agent"

    def run(self, arg1, arg2=None) -> dict:
        # Signature-sensing logic
        # Legacy: run(state, report_snapshot)
        # New: run(report, student=None)
        from models.learner_state import LearnerState
        from models.student import StudentInput

        if isinstance(arg1, (LearnerState, StudentInput)):
            student = arg1
            report = arg2
        elif isinstance(arg2, (LearnerState, StudentInput)):
            report = arg1
            student = arg2
        elif isinstance(arg2, dict) and not isinstance(arg1, dict):
            student = arg1
            report = arg2
        elif isinstance(arg1, dict) and ("weakness_analysis" in arg1 or "study_plan" in arg1):
            report = arg1
            student = arg2
        else:
            if hasattr(arg1, "subjects") and not hasattr(arg1, "weakness_analysis"):
                student = arg1
                report = arg2
            else:
                report = arg1
                student = arg2

        flaws: List[str] = []
        improvements: List[str] = []

        # Get student info
        student_name = "Student"
        student_level = "university"
        weakest_subject = ""
        degree = ""
        subject_confidence = {}
        student_stream = ""
        
        if student:
            student_name = getattr(student, "learner_name", getattr(student, "name", "Student"))
            student_level = getattr(student, "learner_level", "university")
            weakest_subject = getattr(student, "weakest_subject", "")
            degree = getattr(student, "degree", "")
            student_stream = getattr(student, "stream", "")
            
            if hasattr(student, "subject_confidence"):
                subject_confidence = student.subject_confidence
            elif hasattr(student, "subjects"):
                subject_confidence = {s.name: getattr(s, "confidence", 0.75) or 0.75 for s in student.subjects}
            
            if not weakest_subject and hasattr(student, "subjects") and student.subjects:
                weakest_s = min(student.subjects, key=lambda s: s.percentage)
                weakest_subject = weakest_s.name

        reasoning_trace: List[str] = [
            f"Reviewed report for learner {student_name} ({student_level})",
            f"Canonical weakest subject: {weakest_subject}",
            "Checked cross-agent alignment, template risk, and explainability depth",
        ]

        if isinstance(report, dict):
            report_snapshot = report
        else:
            from agents.intelligence import serializable_report
            report_snapshot = serializable_report(report)

        weakness = report_snapshot.get("weakness_analysis", {})
        study_plan = report_snapshot.get("study_plan", {})
        plan = study_plan
        risk_data = report_snapshot.get("risk_assessment", {})
        risk = risk_data
        resources = report_snapshot.get("resources", {})
        career_data = report_snapshot.get("career_readiness", {})
        career = career_data
        consistency = report_snapshot.get("consistency", {})

        # Existing checks modified to use local variables
        weak_subjects = [a["subject"] for a in weakness.get("all_analyses", []) if a.get("classification") == "weak"]
        planned_names = [
            subject["name"]
            for day in plan.get("daily_schedule", [])[:7]
            for subject in day.get("subjects", [])
        ]

        if weakest_subject and weakest_subject not in planned_names[:14]:
            flaws.append(f"Canonical weakest subject {weakest_subject} is under-represented in the first two weeks")
            improvements.append(f"Increase early recurrence for {weakest_subject}")

        for weak_subject in weak_subjects:
            if planned_names.count(weak_subject) < 2 and plan.get("daily_schedule"):
                flaws.append(f"{weak_subject} may not be repeated enough in the first week")
                improvements.append(f"Increase first-week recurrence for {weak_subject}")

        if consistency.get("consistency_score", 100) < 80:
            flaws.append(f"Cross-agent consistency only {consistency.get('consistency_score')}%")
            improvements.append("Reconcile agent outputs against shared LearnerState")

        if career.get("detected_stream") and degree and student_level == "university":
            if career.get("degree") != degree:
                flaws.append("Career output does not echo selected degree in top-level fields")
                improvements.append("Surface degree and specialization in career recommendation header")

        traces = [
            weakness.get("reasoning_trace"),
            plan.get("reasoning_trace"),
            risk.get("reasoning_trace"),
        ]
        if any(len(t or []) < 2 for t in traces):
            flaws.append("One or more agents returned shallow reasoning traces")
            improvements.append("Expand reasoning traces with learner-specific evidence")

        daily_signatures = [
            tuple(subject["name"] for subject in day.get("subjects", []))
            for day in plan.get("daily_schedule", [])[:7]
        ]
        if len(daily_signatures) > 1 and len(set(daily_signatures)) == 1:
            flaws.append("First-week study plan repeats the same subject sequence every day")
            improvements.append("Rotate subjects and focus modes to make the first week visibly adaptive")

        generic_focus = sum(
            1
            for day in plan.get("daily_schedule", [])[:5]
            for sub in day.get("subjects", [])
            for focus in sub.get("focus_areas", [])
            if "Record day" in focus
        )
        if generic_focus > len(weak_subjects) * 3:
            flaws.append("Study plan contains repetitive template focus lines")
            improvements.append("Vary focus modes using learner profile and exam proximity")

        if not resources.get("synthetic_iq"):
            flaws.append("Resource finder did not cite synthetic IQ grounding")
            improvements.append("Attach knowledge-base answer and sources to resources")

        confidence_avg = sum(subject_confidence.values()) / max(len(subject_confidence), 1) if subject_confidence else 0.75
        if confidence_avg < 0.55 and career.get("career_recommendation", {}).get("career_match_score", 0) > 80:
            flaws.append("High career match despite low learner confidence — recommendation may be overconfident")
            improvements.append("Lower career match or add remediation prerequisite")

        # 1. Foundry IQ connection status
        try:
            from foundry.client import FoundryIQClient
            if not FoundryIQClient().is_live():
                flaws.append(
                    "Foundry IQ running in synthetic mode — "
                    "recommendations are not live-grounded"
                )
        except Exception:
            pass

        # 2. High-risk subjects with insufficient study hours
        for risk_item in risk_data.get("subject_risks", []):
            if risk_item.get("risk_level") == "critical":
                subject = risk_item.get("subject", "")
                plan_subjects = [
                    s.get("name") for day in study_plan.get("daily_schedule", [])
                    for s in day.get("subjects", [])
                ]
                hours = sum(
                    s.get("hours", 0)
                    for day in study_plan.get("daily_schedule", [])[:7]
                    for s in day.get("subjects", [])
                    if s.get("name") == subject
                )
                if hours < 5:
                    flaws.append(
                        f"{subject} is critical risk but only {hours:.1f}h "
                        f"planned in first 7 days — needs minimum 10h"
                    )

        # 3. Career relevance check
        detected = career_data.get("detected_stream", "")
        if detected and student_stream and detected.lower() not in student_stream.lower():
            flaws.append(
                f"Career stream mismatch: detected '{detected}' "
                f"but student stream is '{student_stream}'"
            )

        if not flaws:
            flaws.append("Synthetic Foundry IQ is simulated; live Foundry IQ retrieval is not connected yet")
            improvements.append("Connect approved live Foundry IQ retrieval after demo credentials are available")
            reasoning_trace.append("No blocking plan flaw detected; recorded residual demo limitation")

        confidence = 0.88 if len(flaws) <= 1 else max(0.55, 0.88 - len(flaws) * 0.05)
        result = {
            "flaws": flaws,
            "suggested_improvements": improvements,
            "contradictions_found": len([f for f in flaws if "consistency" in f.lower() or "under-represented" in f.lower()]),
        }
        result.update(agent_envelope(
            "Critic identified plan quality issues." if flaws else "Critic found no blocking issues.",
            reasoning_trace,
            confidence,
            self.name,
            ["Approve without checking agent outputs"],
            "The critic challenges generic or contradictory multi-agent output using canonical learner state.",
            evidence=["Pipeline Consistency Check", "Logic Alignment DB"],
        ))
        return result
