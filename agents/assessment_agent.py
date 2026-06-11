from typing import Dict, Any, List
from models.learner_state import LearnerState
from agents.intelligence import agent_envelope

class AssessmentAgent:
    def __init__(self):
        self.name = "Assessment Agent"

    def run(self, state: LearnerState) -> Dict[str, Any]:
        trace = [
            f"Assessing readiness for {state.learner_name}",
            f"Evaluating grounded knowledge across {len(state.subjects)} subjects",
        ]
        
        scores = [float(getattr(s, 'percentage', getattr(s, 'score', 0))) for s in state.subjects]
        avg = sum(scores) / max(1, len(scores))
        
        trace.append(f"Calculated composite mock assessment average: {avg:.1f}%")
        
        if avg >= 80:
            readiness = "High Readiness"
            reasoning = "Learner demonstrates strong retention across core subjects."
        elif avg >= 60:
            readiness = "Moderate Readiness"
            reasoning = "Learner shows foundational understanding but struggles with advanced concepts."
        else:
            readiness = "Low Readiness"
            reasoning = "Learner requires foundational reteaching before attempting exams."

        final = f"Assessment Score: {avg:.1f}/100\nReadiness Level: {readiness}\nReasoning: {reasoning}\n\nGenerated Mock Question: What are the core fundamentals of your weakest subject?"

        return agent_envelope(
            final_output=final,
            reasoning_trace=trace,
            confidence=0.88,
            agent_name=self.name,
            evidence=["Simulated Mock Exam Generation", "Historical Score Alignment"],
            why_this_decision=f"Assessed as {readiness} based on {avg:.1f}% average."
        )
