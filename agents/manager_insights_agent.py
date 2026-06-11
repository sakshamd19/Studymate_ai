from typing import Dict, Any, List
from models.learner_state import LearnerState
from agents.intelligence import agent_envelope

class ManagerInsightsAgent:
    def __init__(self):
        self.name = "Manager Insights Agent"

    def run(self, state: LearnerState) -> Dict[str, Any]:
        trace = [
            f"Compiling manager insights for {state.learner_name}",
            f"Aggregating risk vectors and performance metrics",
        ]
        
        weak_count = sum(1 for s in state.subjects if float(getattr(s, 'percentage', getattr(s, 'score', 100))) < 60)
        
        if weak_count > 0:
            insight = f"Learner has {weak_count} high-risk subjects. Recommend immediate tutor intervention."
            action = "Assign remedial modules and notify mentor."
        else:
            insight = "Learner is performing at or above baseline across all tracked subjects."
            action = "Unlock advanced curriculum tracks."
            
        trace.append(f"Insight determined: {insight}")

        final = f"Manager Summary: {insight}\nRecommended Action: {action}"

        return agent_envelope(
            final_output=final,
            reasoning_trace=trace,
            confidence=0.95,
            agent_name=self.name,
            evidence=["Pipeline Metric Aggregation", "Risk Predictor Heuristics"],
            why_this_decision="Manager insight generated based on subject risk distribution."
        )
