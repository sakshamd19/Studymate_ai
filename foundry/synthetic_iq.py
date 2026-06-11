import json
from pathlib import Path
from typing import Dict, List


class SyntheticFoundryIQ:
    def __init__(self, kb_path: str = "data/knowledge_base.json"):
        self.kb_path = Path(kb_path)
        self.knowledge = json.loads(self.kb_path.read_text()) if self.kb_path.exists() else {"entries": []}

    def query(
        self,
        subject: str,
        learner_level: str,
        classification: str,
        degree: str = "",
        specialization: str = "",
    ) -> Dict:
        subject_l = subject.lower()
        level_l = learner_level.lower()
        degree_l = (degree or "").lower()
        spec_l = (specialization or "").lower()
        matches: List[Dict] = []
        for entry in self.knowledge.get("entries", []):
            if entry.get("subject", "").lower() in subject_l or subject_l in entry.get("subject", "").lower():
                matches.append(entry)
            elif entry.get("learner_level", "").lower() == level_l:
                matches.append(entry)

        if not matches:
            matches = self.knowledge.get("entries", [])[:1]

        selected = matches[0] if matches else {}
        answer = selected.get(
            "answer",
            f"Use synthetic grounded guidance for {subject}: diagnose weak topics, practice, then revise.",
        )
        if classification == "weak":
            answer = f"{answer} Prioritize guided practice and daily retrieval because the subject is WEAK."
        elif classification == "moderate":
            answer = f"{answer} Use balanced revision because the subject is MODERATE."
        else:
            answer = f"{answer} Use weekly spaced revision because the subject is STRONG."
        if degree:
            answer = f"{answer} Align with {degree} coursework expectations."
        if specialization:
            answer = f"{answer} Connect practice to {specialization} specialization outcomes."

        return {
            "answer": answer,
            "sources": selected.get("sources", ["Synthetic Guide", "Mock Dataset"]),
            "degree": degree,
            "specialization": specialization,
            "learner_level": learner_level,
        }
