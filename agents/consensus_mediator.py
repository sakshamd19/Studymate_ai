"""Agent Consensus Mediator — collects opinions, resolves conflicts, explains decisions."""
from typing import Dict, List, Any
from dataclasses import dataclass

from i18n import get_language_manager
from models.learner_state import LearnerState


@dataclass
class AgentOpinion:
    agent_name: str
    opinion: str
    confidence: float
    reasoning: str
    evidence: Dict[str, Any]


class ConsensusMediator:
    def __init__(self):
        self.name = "Consensus Mediator"
        self.lang_manager = get_language_manager()

    def mediate_weakest_subject(self, state: LearnerState, weakness_analysis: Dict, risk_assessment: Dict, study_plan: Dict) -> Dict:
        weakest = state.weakest_subject
        if not weakest:
            return {"topic": "Weakest Subject", "opinions": [], "consensus": "No subjects to assess", "conflicts": []}

        opinions: List[AgentOpinion] = []
        weak_row = next((a for a in weakness_analysis.get("all_analyses", []) if a.get("subject") == weakest), {})
        risk_row = next((r for r in risk_assessment.get("subject_risks", []) if r.get("subject") == weakest), {})
        week_hours = sum(
            sub.get("hours", 0)
            for day in study_plan.get("daily_schedule", [])[:7]
            for sub in day.get("subjects", [])
            if sub.get("name") == weakest
        )

        if weak_row:
            opinions.append(AgentOpinion(
                agent_name="Weakness Analyzer",
                opinion=f"{weakest} is the highest-priority weak area ({weak_row.get('percentage')}%)",
                confidence=float(weak_row.get("confidence", 0.8)) * 100 if weak_row.get("confidence", 0) <= 1 else float(weak_row.get("confidence", 80)),
                reasoning="Canonical PriorityEngine ranking",
                evidence={"priority_score": weak_row.get("priority_score"), "classification": weak_row.get("classification")},
            ))

        if risk_row:
            opinions.append(AgentOpinion(
                agent_name="Risk Predictor",
                opinion=f"{weakest} risk is {risk_row.get('risk_score')}% ({risk_row.get('risk_level')})",
                confidence=float(risk_row.get("confidence_score", 80)),
                reasoning=risk_row.get("reason", "Risk from score, confidence, and exam proximity"),
                evidence={"risk_score": risk_row.get("risk_score"), "days_left": risk_row.get("days_until_exam")},
            ))

        planner_confidence = 72 if week_hours >= 10 else 58
        opinions.append(AgentOpinion(
            agent_name="Study Planner",
            opinion=f"Allocated {week_hours}h in week 1 to {weakest}",
            confidence=planner_confidence,
            reasoning="Higher hours for weakest subject in first-week schedule",
            evidence={"week_one_hours": week_hours, "profile": study_plan.get("learner_profile")},
        ))

        conflicts = []
        if risk_row and study_plan.get("learner_profile") == "strong_learner" and risk_row.get("risk_level") == "high":
            conflicts.append({
                "agents": ["Risk Predictor", "Study Planner"],
                "issue": "Risk is HIGH but planner profile suggests lighter load",
                "resolution": f"Prioritize {weakest} remediation hours over profile default",
                "winner": "Risk Predictor",
                "rejected_alternatives": ["Maintain strong-learner maintenance-only plan"],
            })

        return {
            "topic": f"Weakest Subject Priority: {weakest}",
            "opinions": [self._serialize_opinion(op) for op in opinions],
            "consensus": self._calculate_consensus(opinions),
            "agreement_level": self._calculate_agreement_level(opinions),
            "conflicts": conflicts,
            "resolution": conflicts[0]["resolution"] if conflicts else f"All agents align on prioritizing {weakest}",
            "winner": conflicts[0]["winner"] if conflicts else "Weakness Analyzer",
        }

    def mediate_career_suitability(self, state: LearnerState, career_readiness: Dict, risk_assessment: Dict) -> Dict:
        career_rec = career_readiness.get("career_recommendation", {})
        career_title = career_rec.get("career", "Unknown")
        opinions: List[AgentOpinion] = []
        match_score = career_rec.get("career_match_score") or 70

        opinions.append(AgentOpinion(
            agent_name="Career Readiness Agent",
            opinion=f"{career_title} match score {match_score}",
            confidence=min(95, match_score),
            reasoning=career_rec.get("why_this_path", "Degree, specialization, and skill profile"),
            evidence={"degree": state.degree, "specialization": state.specialization},
        ))

        if state.weakest_subject:
            opinions.append(AgentOpinion(
                agent_name="Weakness Analyzer (Career Perspective)",
                opinion=f"Weakest subject {state.weakest_subject} affects readiness",
                confidence=70 if state.weakest_subject.lower() not in {"mathematics", "math", "maths"} else 55,
                reasoning="Core subject gaps reduce career match for technical paths",
                evidence={"weakest_subject": state.weakest_subject},
            ))

        high_risk = [r for r in risk_assessment.get("subject_risks", []) if r.get("risk_score", 0) >= 65]
        if high_risk:
            opinions.append(AgentOpinion(
                agent_name="Risk Predictor (Career Perspective)",
                opinion=f"{len(high_risk)} subject(s) at high exam risk may delay career prep",
                confidence=max(45, 100 - len(high_risk) * 15),
                reasoning="Exam recovery should precede aggressive career credentialing",
                evidence={"high_risk_subjects": [r["subject"] for r in high_risk]},
            ))

        conflicts = []
        if match_score >= 75 and state.weakest_subject and state.subject_scores.get(state.weakest_subject, 100) < 60:
            conflicts.append({
                "agents": ["Career Readiness Agent", "Weakness Analyzer"],
                "issue": "High career match despite weak foundation subject",
                "resolution": "Pursue career path with explicit remediation for weakest subject first",
                "winner": "Weakness Analyzer",
                "rejected_alternatives": ["Immediate advanced credential sprint"],
            })

        return {
            "topic": f"Career Suitability: {career_title}",
            "agent_opinions": [self._serialize_opinion(op) for op in opinions],
            "consensus": self._calculate_consensus(opinions),
            "recommendation": career_rec.get("next_step", "Build skills incrementally"),
            "caveats": self._identify_agreement_gaps(opinions),
            "conflicts": conflicts,
            "resolution": conflicts[0]["resolution"] if conflicts else f"Career path {career_title} is consistent with learner profile",
            "winner": conflicts[0]["winner"] if conflicts else "Career Readiness Agent",
        }

    def _serialize_opinion(self, op: AgentOpinion) -> Dict:
        return {
            "agent": op.agent_name,
            "opinion": op.opinion,
            "confidence": op.confidence,
            "reasoning": op.reasoning,
            "evidence": op.evidence,
        }

    def _calculate_consensus(self, opinions: List[AgentOpinion]) -> str:
        if not opinions:
            return "No consensus (no opinions provided)"
        avg_confidence = sum(op.confidence for op in opinions) / len(opinions)
        if avg_confidence >= 80:
            return f"STRONG CONSENSUS ({avg_confidence:.0f}% avg confidence)"
        if avg_confidence >= 65:
            return f"MODERATE CONSENSUS ({avg_confidence:.0f}% avg confidence)"
        if avg_confidence >= 50:
            return f"WEAK CONSENSUS ({avg_confidence:.0f}% avg confidence)"
        return f"NO CONSENSUS ({avg_confidence:.0f}% avg confidence)"

    def _calculate_agreement_level(self, opinions: List[AgentOpinion]) -> float:
        if len(opinions) < 2:
            return 100.0
        return sum(op.confidence for op in opinions) / len(opinions)

    def _identify_agreement_gaps(self, opinions: List[AgentOpinion]) -> List[str]:
        return [
            f"{op.agent_name}: {op.confidence:.0f}% confident — {op.reasoning}"
            for op in opinions
            if op.confidence < 70
        ]

    def generate_full_consensus_report(self, report: Dict, state: LearnerState) -> Dict:
        consensus_report = {
            "agents_engaged": 6,
            "consensus_areas": [],
            "disagreement_areas": [],
            "agent_opinions": [],
            "conflicts": [],
            "overall_confidence": 0,
            "resolution": "",
            "winner": "",
        }

        if report.get("weakness_analysis") and report.get("risk_assessment"):
            weakest_block = self.mediate_weakest_subject(
                state,
                report["weakness_analysis"],
                report["risk_assessment"],
                report.get("study_plan", {}),
            )
            consensus_report["consensus_areas"].append(weakest_block)
            consensus_report["agent_opinions"].extend(weakest_block.get("opinions", []))
            consensus_report["conflicts"].extend(weakest_block.get("conflicts", []))

        if report.get("career_readiness") and report.get("risk_assessment"):
            career_block = self.mediate_career_suitability(state, report["career_readiness"], report["risk_assessment"])
            consensus_report["consensus_areas"].append(career_block)
            consensus_report["agent_opinions"].extend(career_block.get("agent_opinions", []))
            consensus_report["conflicts"].extend(career_block.get("conflicts", []))

        all_confidences = [op.get("confidence", 0) for op in consensus_report["agent_opinions"]]
        if all_confidences:
            consensus_report["overall_confidence"] = sum(all_confidences) / len(all_confidences)

        if consensus_report["conflicts"]:
            consensus_report["resolution"] = consensus_report["conflicts"][-1].get("resolution", "")
            consensus_report["winner"] = consensus_report["conflicts"][-1].get("winner", "")
        elif state.weakest_subject:
            consensus_report["resolution"] = f"Agents agree to prioritize {state.weakest_subject}"
            consensus_report["winner"] = "Weakness Analyzer"

        return consensus_report
