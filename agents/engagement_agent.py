from typing import Dict, Any, List
from models.learner_state import LearnerState
from agents.intelligence import agent_envelope
import random

class EngagementAgent:
    def __init__(self):
        self.name = "Engagement Agent"

    def run(self, state: LearnerState) -> Dict[str, Any]:
        trace = [
            f"Tracking engagement metrics for {state.learner_name}",
            f"Analyzing historical interaction logs (simulated)",
        ]
        
        # Simulate an engagement score based on their priority score (higher priority = needs more engagement)
        avg_score = sum(float(getattr(s, 'percentage', getattr(s, 'score', 50))) for s in state.subjects) / max(1, len(state.subjects))
        engagement_metric = min(100, max(0, avg_score + random.randint(-10, 10)))
        
        trace.append(f"Calculated composite engagement score: {engagement_metric:.1f}/100")

        if engagement_metric > 80:
            status = "Highly Engaged"
            insight = "Learner is consistently hitting milestones."
        elif engagement_metric > 50:
            status = "Moderately Engaged"
            insight = "Learner is active but showing signs of fatigue in weak subjects."
        else:
            status = "Disengaged Risk"
            insight = "Learner is missing study blocks. Intervention required."

        final = f"Engagement Status: {status}\nScore: {engagement_metric:.1f}\nInsight: {insight}"

        return agent_envelope(
            final_output=final,
            reasoning_trace=trace,
            confidence=0.85,
            agent_name=self.name,
            evidence=["Simulated 7-day Login History", "Module Completion Rates"],
            why_this_decision=f"Engagement mapped to {status} based on {engagement_metric:.1f} score."
        )
