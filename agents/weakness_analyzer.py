from models.student import Subject
from models.learner_state import LearnerState
from agents.intelligence import (
    agent_envelope,
    classification_rank,
    classify_subject,
    confidence_from_signals,
    priority_score,
    subject_confidence,
    subject_trace,
)
from config import config
from typing import Dict, List


class WeaknessAnalyzerAgent:
    def __init__(self):
        self.name = "Weakness Analyzer Agent"
        self.threshold = config.WEAK_SUBJECT_THRESHOLD

    def classify_weakness(self, percentage: float) -> str:
        return classify_subject(percentage)

    def analyze_subject(self, subject, state=None) -> dict:
        student = state
        pct = subject.percentage
        level = self.classify_weakness(pct)

        suggestions = {
            "weak": [
                f"Immediately focus all attention on {subject.name}",
                "Study minimum 3 hours daily with retrieval practice",
                "Focus on weak chapters first",
                "Practice previous year questions daily",
                "Ask a teacher or peer to review mistakes"
            ],
            "moderate": [
                f"Give balanced attention to {subject.name} this week",
                "Revise core concepts and formulas",
                "Solve 10-15 practice questions on alternate days",
                "Use a weekly checkpoint quiz"
            ],
            "strong": [
                f"{subject.name} is strong — protect it with spaced revision",
                "Quick revision once a week is enough",
                "Focus on advanced or tricky edge case questions"
            ]
        }
        confidence = subject_confidence(subject)
        priority = priority_score(subject, confidence)
        trace = subject_trace(subject, level)

        analysis = {
            "subject": subject.name,
            "score": subject.score,
            "total": subject.total_marks,
            "percentage": round(pct, 2),
            "weakness_level": level,
            "classification": level,
            "days_until_exam": subject.days_until_exam,
            "suggestions": suggestions[level],
            "priority_rank": self._get_priority_rank(level),
            "priority_score": priority,
            "reasoning_trace": trace,
            "confidence": confidence,
            "why_this_decision": f"{subject.name} is {level.upper()} because its score is {pct:.1f}% and priority score is {priority}.",
            "rejected_options": [
                other.upper()
                for other in ["weak", "moderate", "strong"]
                if other != level
            ],
            "generated_by": self.name,
        }

        # Foundry IQ enhancement
        try:
            from foundry.client import FoundryIQClient
            from foundry.queries import WEAKNESS_SYSTEM, weakness_query
            _fiq = FoundryIQClient(test_mode=getattr(state, "test_mode", False))
            _q = (
                f"Subject: {subject.name} | Score: {subject.score}/{subject.total_marks} "
                f"({subject.percentage:.1f}%) | Days until exam: {subject.days_until_exam} | "
                f"Student stream: {student.stream if hasattr(student, 'stream') else 'N/A'}\n"
                f"Give 3 specific improvement actions for this weakness."
            )
            
            def safe_chat(fiq_client, context, message, system_prompt):
                import concurrent.futures
                import json
                res = fiq_client.chat(context=context, user_message=message, system_prompt=system_prompt)
                try:
                    # If it returned a JSON string (like deterministic response), parse it
                    if isinstance(res, str) and res.strip().startswith("{"):
                        return json.loads(res)
                    return {"content": res, "confidence": 0.5, "reasoning": "Live API response"}
                except Exception:
                    raw = fiq_client._deterministic_response(system_prompt, message)
                    return json.loads(raw)

            ai_tip = safe_chat(
                _fiq,
                context="weakness_analysis",
                message=_q,
                system_prompt="You are an expert academic weakness analyzer. Be specific and actionable."
            )
            analysis["ai_suggestions"] = ai_tip
            analysis["foundry_iq_grounded"] = _fiq.is_live()
            analysis["foundry_iq_source"] = _fiq.get_source_label()
        except Exception:
            analysis["ai_suggestions"] = None
            analysis["foundry_iq_grounded"] = False
            analysis["foundry_iq_source"] = "error"

        return analysis

    def _get_priority_rank(self, level: str) -> int:
        return classification_rank(level)

    def run(self, state: LearnerState) -> dict:
        student = state
        if not state.subjects:
            result = {
                "student_name": state.learner_name,
                "overall_average": 0,
                "total_subjects": 0,
                "weak_count": 0,
                "moderate_count": 0,
                "strong_count": 0,
                "good_count": 0,
                "all_analyses": [],
                "weak_subjects": [],
                "moderate_subjects": [],
                "strong_subjects": [],
                "good_subjects": [],
                "most_critical": None,
                "weakest_subject": None,
                "ranked_subjects": [],
                "summary": "No subjects found. Please add subjects to analyze."
            }
            result.update(agent_envelope(
                "No subject data available for weakness analysis.",
                ["No subjects were provided", "Returned fail-safe weakness response"],
                0.3,
                evidence=["Missing user input"],
            ))
            return result

        analyses = []
        
        import concurrent.futures
        def _process_weakness_subject(row):
            subject = state.get_subject(row["subject"])
            if not subject:
                return None
            analysis = self.analyze_subject(subject, state)
            analysis["priority_score"] = row["priority_score"]
            analysis["confidence"] = row["confidence"]
            return analysis

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, len(state.priority_ranking))) as executor:
            results = executor.map(_process_weakness_subject, state.priority_ranking)
            for res in results:
                if res:
                    analyses.append(res)

        analyses.sort(key=lambda x: (-x["priority_score"], x["percentage"], x["days_until_exam"], x["subject"]))

        weak_subjects = [a for a in analyses if a["classification"] == "weak"]
        moderate_subjects = [a for a in analyses if a["classification"] == "moderate"]
        strong_subjects = [a for a in analyses if a["classification"] == "strong"]

        overall_avg = sum(s.percentage for s in state.subjects) / len(state.subjects)

        reasoning_trace = [
            f"Ranked {len(analyses)} subjects using shared PriorityEngine",
            f"Weakest subject is {state.weakest_subject} at {analyses[0]['percentage']}%",
            f"Moderate subjects: {', '.join(state.moderate_subjects) or 'none'}",
            f"Strongest subject: {state.strongest_subject}",
            "Applied thresholds: <60 WEAK, 60-75 MODERATE, >75 STRONG",
        ]

        result = {
            "student_name": state.learner_name,
            "overall_average": round(overall_avg, 2),
            "total_subjects": len(state.subjects),
            "weak_count": len(weak_subjects),
            "moderate_count": len(moderate_subjects),
            "strong_count": len(strong_subjects),
            "good_count": len(strong_subjects),
            "all_analyses": analyses,
            "weak_subjects": weak_subjects,
            "moderate_subjects": moderate_subjects,
            "strong_subjects": strong_subjects,
            "good_subjects": strong_subjects,
            "most_critical": analyses[0] if analyses else None,
            "weakest_subject": analyses[0] if analyses else None,
            "ranked_subjects": analyses,
            "summary": self._generate_summary(overall_avg, weak_subjects)
        }
        result.update(agent_envelope(
            result["summary"],
            reasoning_trace,
            confidence_from_signals(0.92, len(analyses) / 8),
            self.name,
            ["Rank by score only", "Rank by exam date only"],
            "Weakest and highest-priority subjects are surfaced first using score, confidence, and exam proximity.",
            evidence=["WeaknessAnalyzer Internal Logic", "Student Score Distribution"],
        ))
        return result

    def _generate_summary(self, avg: float, weak_subjects: List[dict]) -> str:
        if not weak_subjects:
            return "No WEAK subjects detected. Maintain strengths with spaced weekly revision."
        elif avg < config.WEAK_SUBJECT_THRESHOLD:
            return f"Urgent attention needed across {len(weak_subjects)} WEAK subject(s). Immediate action required."
        else:
            return f"{len(weak_subjects)} WEAK subject(s) need targeted improvement. A focused study plan will help."
