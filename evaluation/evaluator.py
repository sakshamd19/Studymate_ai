import time
from typing import Dict, List, Optional

from agents.intelligence import agent_envelope
from models.learner_state import LearnerState


class EvaluationAgent:
    def __init__(self):
        self.name = "Evaluation Agent"

    def run(self, report: Dict, execution_chain: List[Dict], state: Optional[LearnerState] = None) -> dict:
        started = time.perf_counter()

        weakness = report.get("weakness_analysis", {})
        plan = report.get("study_plan", {})
        risk = report.get("risk_assessment", {})
        resources = report.get("resources", {})
        consistency = report.get("consistency", {})
        critic = report.get("critic_review", {})
        counterfactuals = report.get("counterfactuals", {})

        traces_present = all(
            report.get(key, {}).get("reasoning_trace")
            for key in ["weakness_analysis", "study_plan", "risk_assessment", "resources", "career_readiness"]
        )
        weak_block = weakness.get("weakest_subject") or {}
        weak_name = weak_block.get("subject") if isinstance(weak_block, dict) else weak_block
        weakest_aligned = (
            weak_name == (risk.get("most_at_risk") or {}).get("subject")
            == (state.weakest_subject if state else weak_name)
        )
        varied_plan = len({
            tuple(subject.get("name") for subject in day.get("subjects", []))
            for day in plan.get("daily_schedule", [])[:7]
        }) > 1 if plan.get("daily_schedule") else False
        personalized = bool(resources.get("learner_level")) and bool(state and state.degree or state and state.learner_level in {"school", "cbse"})
        if state and state.learner_level in {"school", "cbse"}:
            personalized = bool(resources.get("learner_level"))
        safe = bool(report.get("safety_status", {}).get("is_valid", True))
        consistency_score = consistency.get("consistency_score", 0)
        critic_flaws = len(critic.get("flaws", []))
        cf_actionable = bool(counterfactuals.get("new_risk_if_hours_increase") is not None)

        consistency_metric = min(100, consistency_score)
        personalization_metric = 55
        if state:
            if state.degree or state.specialization:
                personalization_metric += 15
            if state.skill_profile:
                personalization_metric += 10
            if resources.get("learner_level") == state.learner_level:
                personalization_metric += 10
        personalization_metric = min(100, personalization_metric)

        explainability_metric = 40
        if traces_present:
            explainability_metric += 25
        if report.get("consensus", {}).get("agent_opinions"):
            explainability_metric += 15
        if consistency.get("explanation"):
            explainability_metric += 10
        explainability_metric = min(100, explainability_metric)

        reasoning_metric = 45
        if weakest_aligned:
            reasoning_metric += 20
        if cf_actionable:
            reasoning_metric += 15
        if critic.get("reasoning_trace"):
            reasoning_metric += 10
        reasoning_metric = min(100, reasoning_metric)

        robustness_metric = 70 if safe else 20
        if varied_plan:
            robustness_metric += 10
        robustness_metric -= min(30, critic_flaws * 4)
        robustness_metric = max(0, min(100, robustness_metric))

        reliability_metric = round((consistency_metric + robustness_metric + (100 if safe else 0)) / 3, 1)

        legacy = {
            "accuracy_score": round(consistency_metric * 0.25, 1),
            "reasoning_score": round(reasoning_metric * 0.25, 1),
            "creativity_score": round(personalization_metric * 0.15, 1),
            "ux_score": round(explainability_metric * 0.15, 1),
            "reliability_score": round(reliability_metric * 0.20, 1),
        }
        base_score = round(sum(legacy.values()), 1)
        deductions = []

        try:
            from foundry.client import FoundryIQClient
            _fiq = FoundryIQClient()
            if not _fiq.is_live():
                deductions.append(("Foundry IQ not connected — running in synthetic mode", -7))
        except Exception:
            deductions.append(("Foundry IQ client error", -5))

        total_deduction = sum(d[1] for d in deductions)
        overall_score = max(0, round(base_score + total_deduction, 1))

        weaknesses = []
        if not weakest_aligned:
            weaknesses.append("Weakest subject alignment across agents needs improvement")
        if not varied_plan:
            weaknesses.append("Schedule variation could be stronger for longer plans")
        if consistency_score < 80:
            weaknesses.append(f"Consistency score {consistency_score}% below target")
        if critic_flaws > 2:
            weaknesses.append(f"Critic flagged {critic_flaws} quality issues")

        latency_ms = round((time.perf_counter() - started) * 1000, 2)
        result = {
            "consistency_score": consistency_metric,
            "explainability_score": explainability_metric,
            "reasoning_quality_score": reasoning_metric,
            "reliability_score": reliability_metric,
            "agent_execution_chain": execution_chain,
            "latency_per_agent_ms": {entry["agent"]: entry["latency_ms"] for entry in execution_chain},
            "evaluator_latency_ms": latency_ms,
            "system_weaknesses": weaknesses,
            "deductions": deductions,
            "improvement_suggestions": [
                "Connect FOUNDRY_API_KEY at ai.azure.com for live Microsoft Foundry IQ retrieval",
                "Record and attach demo video before June 14 submission deadline",
                "Create project on innovationstudio.microsoft.com before June 14",
                "Add longitudinal learner history once synthetic benchmark data is approved",
            ],
            "evidence": {
                "weakest_aligned": weakest_aligned,
                "consistency_score": consistency_score,
                "critic_flaws": critic_flaws,
                "varied_plan": varied_plan,
                "traces_present": traces_present,
            },
        }
        result.update(agent_envelope(
            f"Evidence-based evaluation completed — overall {overall_score}/100.",
            [
                "Checked agent outputs against observed behavior",
                f"Scored consistency {consistency_metric}% from cross-agent validator",
                f"Scored personalization {personalization_metric}% from degree/level/skill usage",
                f"Scored explainability {explainability_metric}% from traces and consensus visibility",
                f"Logged latency for {len(execution_chain)} agent execution steps",
                f"Critic flaws counted: {critic_flaws}",
            ],
            min(0.95, overall_score / 100),
            self.name,
            ["Assign high scores without behavioral evidence"],
            "Scores are derived from observed agent behavior, not self-congratulation.",
        ))
        return result
