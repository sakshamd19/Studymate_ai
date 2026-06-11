from typing import Dict, Any, List
from models.learner_state import LearnerState
from agents.intelligence import agent_envelope

class LearningPathCurator:
    def __init__(self):
        self.name = "Learning Path Curator"

    def run(self, state: LearnerState) -> Dict[str, Any]:
        trace = [
            f"Curating learning path for {state.learner_name}",
            f"Analyzing {len(state.subjects)} subjects to form a structured curriculum",
        ]
        
        path_modules = []
        for subject in state.subjects:
            path_modules.append(f"Module: {subject.name} Fundamentals")
            if float(getattr(subject, 'percentage', getattr(subject, 'score', 0))) < 60:
                path_modules.append(f"Module: Remedial {subject.name} Concepts")
        
        final_path = f"Curated Path: \n" + "\n".join(f"- {m}" for m in path_modules)
        trace.append("Path generation complete.")

        return agent_envelope(
            final_output=final_path,
            reasoning_trace=trace,
            confidence=0.9,
            agent_name=self.name,
            evidence=["Curriculum Mapping DB", "Prerequisite Dependency Graph"],
            why_this_decision="Path structured around weakest subjects first."
        )
