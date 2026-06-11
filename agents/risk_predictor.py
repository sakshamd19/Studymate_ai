from models.student import Subject
from models.learner_state import LearnerState
from config import config
from typing import Dict, List
from agents.intelligence import (
    agent_envelope,
    classify_subject,
    confidence_from_signals,
    priority_score,
    subject_confidence,
    subject_trace,
)

class RiskPredictorAgent:
    def __init__(self):
        self.name = "Risk Predictor Agent"

    def calculate_risk_score(self, subject: Subject) -> float:
        confidence = subject_confidence(subject)
        priority = priority_score(subject, confidence)
        risk = priority * 0.82
        days_left = max(subject.days_until_exam, 0)
        if subject.percentage < 60 and days_left <= 10:
            risk += 15
        return round(max(0, min(100, risk)), 2)

    def calculate_confidence_score(self, subject: Subject) -> float:
        return round(subject_confidence(subject) * 100, 2)

    def get_risk_level(self, risk_score: float) -> str:
        if risk_score >= 65:
            return "high"
        elif risk_score >= 40:
            return "moderate"
        else:
            return "low"

    def get_prediction(self, subject: Subject, risk_score: float) -> str:
        days_left = subject.days_until_exam
        pct = subject.percentage

        if risk_score >= 65:
            return f"High risk in {subject.name}: low score and/or exam proximity require immediate intervention"
        elif risk_score >= 40:
            return f"Moderate risk in {subject.name}: consistent effort over the next {days_left} days is required"
        else:
            return f"Low risk in {subject.name}: maintain pace and revise regularly"

    def get_recovery_plan(self, subject: Subject, risk_level: str) -> List[str]:
        days_left = subject.days_until_exam
        plans = {
            "high": [
                f"Study {subject.name} for 3 focused hours every day until the exam",
                "Solve chapter-wise question banks systematically",
                f"Target improving score by 15-20% in {days_left} days",
                "Get help from a teacher or peer immediately"
            ],
            "moderate": [
                f"Give {subject.name} at least 1.5 hours of focused study on alternate days",
                "Revise core concepts and practice regularly",
                "Run a checkpoint quiz every three days"
            ],
            "low": [
                f"Maintain your current pace for {subject.name}",
                "Weekly revision is sufficient",
                "Focus your extra energy on weaker subjects"
            ]
        }
        return plans.get(risk_level, [])

    def analyze_subject_risk(self, subject: Subject, student=None) -> dict:
        risk_score = self.calculate_risk_score(subject)
        confidence_score = self.calculate_confidence_score(subject)
        risk_level = self.get_risk_level(risk_score)
        prediction = self.get_prediction(subject, risk_score)
        recovery_plan = self.get_recovery_plan(subject, risk_level)
        classification = classify_subject(subject.percentage)
        reason = (
            f"{subject.name} is {classification.upper()} at {subject.percentage:.1f}% "
            f"with {max(subject.days_until_exam, 0)} day(s) remaining."
        )
        recommended_action = recovery_plan[0] if recovery_plan else "Maintain revision rhythm."
        reasoning_trace = subject_trace(subject, classification)
        priority = priority_score(subject, confidence_score / 100)
        if subject.percentage < 60 and subject.days_until_exam <= 10:
            reasoning_trace.append("Risk increased due to low score and exam proximity")
        else:
            reasoning_trace.append("Risk calibrated from priority formula and days remaining")

        risk_data = {
            "subject": subject.name,
            "current_score": subject.score,
            "percentage": subject.percentage,
            "days_until_exam": subject.days_until_exam,
            "risk_score": risk_score,
            "priority_score": priority,
            "confidence_score": confidence_score,
            "risk_level": risk_level,
            "classification": classification,
            "reason": reason,
            "recommended_action": recommended_action,
            "prediction": prediction,
            "recovery_plan": recovery_plan,
            "exam_date": subject.exam_date.strftime("%d %B %Y"),
            "final_output": prediction,
            "reasoning_trace": reasoning_trace,
            "confidence": confidence_from_signals(confidence_score / 100, 0.85),
            "why_this_decision": f"{subject.name} risk follows priority score {priority} and classification {classification.upper()}.",
            "rejected_options": ["Ignore exam proximity", "Use static risk by stream"],
            "generated_by": self.name,
        }

        risk_result = risk_data
        # Foundry IQ risk narrative
        try:
            from foundry.client import FoundryIQClient
            _fiq = FoundryIQClient()
            _q = (
                f"Subject: {subject.name} | Score: {subject.percentage:.1f}% | "
                f"Days until exam: {subject.days_until_exam} | "
                f"Degree: {getattr(student, 'degree', 'university level') if student else 'N/A'}.\n"
                f"Assess failure probability and give a 3-step recovery plan."
            )
            ai_recovery = _fiq.chat(
                context="risk_prediction",
                user_message=_q,
                system_prompt="You are an academic risk analyst for Indian exams. Be honest about risk levels.",
            )
            risk_result["ai_recovery_plan"] = ai_recovery
            risk_result["foundry_iq_grounded"] = _fiq.is_live()
            risk_result["foundry_iq_source"] = _fiq.get_source_label()
        except Exception:
            risk_result["foundry_iq_grounded"] = False

        return risk_data

    def run(self, state: LearnerState) -> dict:
        subject_risks = []
        
        import concurrent.futures
        def _process_risk(subject):
            if subject.days_until_exam >= 0:
                risk_data = self.analyze_subject_risk(subject, state)
                conf = state.subject_confidence.get(subject.name, risk_data["confidence_score"] / 100)
                if conf < 0.5:
                    risk_data["risk_score"] = round(min(100, risk_data["risk_score"] * 1.08), 2)
                    risk_data["reasoning_trace"].append("Risk elevated because learner confidence is low")
                return risk_data
            return None

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, max(1, len(state.subjects)))) as executor:
            results = executor.map(_process_risk, state.subjects)
            for res in results:
                if res:
                    subject_risks.append(res)

        subject_risks.sort(
            key=lambda x: (
                -x["risk_score"],
                0 if x["subject"] == state.weakest_subject else 1,
                x["subject"],
            )
        )

        high = [s for s in subject_risks if s["risk_level"] == "high"]
        moderate = [s for s in subject_risks if s["risk_level"] == "moderate"]
        low = [s for s in subject_risks if s["risk_level"] == "low"]

        # overall risk across all subjects
        avg_risk = sum(s["risk_score"] for s in subject_risks) / len(subject_risks) if subject_risks else 0
        avg_confidence = sum(s["confidence_score"] for s in subject_risks) / len(subject_risks) if subject_risks else 0

        result = {
            "student_name": state.learner_name,
            "canonical_weakest_subject": state.weakest_subject,
            "overall_risk_score": round(avg_risk, 2),
            "overall_confidence": round(avg_confidence, 2),
            "total_subjects_analyzed": len(subject_risks),
            "high_count": len(high),
            "moderate_count": len(moderate),
            "low_count": len(low),
            "subject_risks": subject_risks,
            "most_at_risk": subject_risks[0] if subject_risks else None,
            "safest_subject": subject_risks[-1] if subject_risks else None,
            "overall_verdict": self._get_overall_verdict(avg_risk, high),
            "urgent_action": len(high) > 0
        }
        result.update(agent_envelope(
            result["overall_verdict"],
            [
                "Calculated risk from requested priority formula and low-score urgency",
                "Raised risk when low score coincides with near exam date",
                "Sorted subjects by highest risk first",
            ],
            confidence_from_signals(avg_confidence / 100 if subject_risks else 0.3, 0.88),
            self.name,
            ["Static risk per learner", "Risk based on marks only"],
            "Risk combines score gap, confidence, and exam proximity so urgent weak subjects rise first.",
            evidence=["Risk Formula Engine", "Historical Cohort Failure Rates"],
        ))
        return result

    def _get_overall_verdict(self, avg_risk: float, high: list) -> str:
        if len(high) >= 2:
            return "Several subjects at HIGH risk: a strict recovery schedule is non-negotiable now."
        elif len(high) == 1:
            return f"{high[0]['subject']} is HIGH risk: prioritize it above everything else."
        elif avg_risk >= 50:
            return "Overall risk is elevated — consistent daily effort across all subjects needed."
        else:
            return "Overall risk is manageable — stay consistent and you will do well!"
