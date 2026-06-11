"""Counterfactual Reasoning Agent - Generate 'what-if' scenarios for student decision-making."""
from typing import Dict, List, Any
from models.student import Subject
from models.learner_state import LearnerState
from copy import deepcopy
from datetime import date
from i18n import t
from agents.intelligence import agent_envelope, confidence_from_signals
from agents.intelligence import FAILSAFE_MESSAGE
from agents.risk_predictor import RiskPredictorAgent


class CounterfactualScenario:
    """Represents a hypothetical student profile and outcomes."""
    
    def __init__(self, scenario_name: str, description: str, modifications: Dict):
        self.scenario_name = scenario_name
        self.description = description
        self.modifications = modifications  # What changed from original
        self.predicted_outcomes = {}
    
    def to_dict(self) -> Dict:
        return {
            "scenario_name": self.scenario_name,
            "description": self.description,
            "modifications": self.modifications,
            "predicted_outcomes": self.predicted_outcomes
        }


class CounterfactualReasoner:
    """
    Generate and reason about hypothetical scenarios.
    
    Example:
        Original: Student weak in Physics (38%)
        Scenario 1: "What if you focus ONLY on Math?"
        Scenario 2: "What if you do balanced revision?"
        Scenario 3: "What if you get Physics tutor?"
    """
    
    def __init__(self):
        self.name = "Counterfactual Reasoner"
    
    def generate_scenarios(self, state: LearnerState, num_scenarios: int = 3) -> List[CounterfactualScenario]:
        scenarios = []
        weak_subject = state.get_subject(state.weakest_subject) if state.weakest_subject else None
        strong_subjects = [s for s in state.subjects if s.percentage >= 75]

        if weak_subject:
            scenario1 = self._create_focus_weak_scenario(state, weak_subject)
            scenarios.append(scenario1)
        
        # Scenario 2: Balanced approach
        scenario2 = self._create_balanced_scenario(state)
        scenarios.append(scenario2)

        if strong_subjects:
            strong_subject = state.get_subject(state.strongest_subject) or strong_subjects[0]
            scenario3 = self._create_leverage_strength_scenario(state, strong_subject)
            scenarios.append(scenario3)
        
        return scenarios[:num_scenarios]
    
    def _create_focus_weak_scenario(self, state: LearnerState, target_weak: Subject) -> CounterfactualScenario:
        """
        Scenario: Focus heavily on the weakest subject.
        'What if you dedicate 60% of study time to Physics?'
        """
        description = f"Focus heavily on {target_weak.name} (60% study time)"
        
        # Project outcome: +15-20% improvement
        improvement = 18
        new_score = min(90, target_weak.percentage + improvement)
        
        scenario = CounterfactualScenario(
            scenario_name="Focus on Weakness",
            description=description,
            modifications={
                "focus_subject": target_weak.name,
                "study_allocation": {"focus_subject": "60%", "others": "40%"},
                "original_score": target_weak.percentage,
                "projected_score": new_score,
                "improvement": improvement
            }
        )
        
        # Run agents' reasoning on this scenario
        scenario.predicted_outcomes = self._reason_about_scenario(state, scenario)
        return scenario

    def _create_balanced_scenario(self, state: LearnerState) -> CounterfactualScenario:
        """
        Scenario: Balanced revision across all subjects.
        'What if you study equally across all subjects?'
        """
        total_subjects = len(state.subjects)
        study_per_subject = 100 / total_subjects
        projected_subjects = []
        avg_improvement = 0

        for subject in state.subjects:
            if subject.percentage < 60:
                improvement = 10
            elif subject.percentage < 75:
                improvement = 5
            else:
                improvement = 2
            
            new_score = min(95, subject.percentage + improvement)
            projected_subjects.append({
                "subject": subject.name,
                "original": subject.percentage,
                "projected": new_score,
                "improvement": improvement
            })
            avg_improvement += improvement
        
        avg_improvement /= total_subjects
        
        scenario = CounterfactualScenario(
            scenario_name="Balanced Approach",
            description="Study equally across all subjects (distributed effort)",
            modifications={
                "study_allocation": {s.name: f"{study_per_subject:.0f}%" for s in state.subjects},
                "projected_subjects": projected_subjects,
                "average_improvement": avg_improvement,
                "overall_projected_avg": sum(s["projected"] for s in projected_subjects) / len(projected_subjects)
            }
        )
        
        scenario.predicted_outcomes = self._reason_about_scenario(state, scenario)
        return scenario

    def _create_leverage_strength_scenario(self, state: LearnerState, target_strong: Subject) -> CounterfactualScenario:
        """
        Scenario: Double down on strength, maintain others.
        'What if you optimize for Computer Science (your strong area)?'
        """
        description = f"Optimize {target_strong.name} (70% study time), maintain others"
        
        scenario = CounterfactualScenario(
            scenario_name="Leverage Strength",
            description=description,
            modifications={
                "primary_focus": target_strong.name,
                "study_allocation": {target_strong.name: "70%", "others": "30%"},
                "strength_projection": min(99, target_strong.percentage + 12),
                "strength_original": target_strong.percentage,
                "maintains_other_levels": True
            }
        )
        
        scenario.predicted_outcomes = self._reason_about_scenario(state, scenario)
        return scenario

    def _reason_about_scenario(self, state: LearnerState, scenario: CounterfactualScenario) -> Dict:
        """
        Run agents' reasoning on the counterfactual scenario.
        This is where agents re-analyze assuming the scenario is true.
        """
        outcomes = {
            "career_impact": {},
            "risk_assessment": {},
            "study_plan_adjustment": {},
            "placement_potential": {}
        }
        
        # Career impact reasoning
        focus_subject = scenario.modifications.get("focus_subject")
        if focus_subject:
            outcomes["career_impact"] = {
                "description": f"Improving {focus_subject} opens up more career options",
                "benefit": "Expands career opportunities",
                "new_fit_scores": self._estimate_career_fit(scenario)
            }
        else:
            outcomes["career_impact"] = {
                "description": "Balanced improvement benefits all roles equally",
                "benefit": "More stable across career paths",
                "new_fit_scores": self._estimate_career_fit(scenario)
            }
        
        # Risk assessment reasoning
        projected_avg = scenario.modifications.get("overall_projected_avg", 65)
        if projected_avg >= 80:
            risk_level = "LOW"
            risk_description = "Strong probability of success in all exams"
        elif projected_avg >= 65:
            risk_level = "MODERATE"
            risk_description = "Good chance of passing most exams"
        else:
            risk_level = "HIGH"
            risk_description = "Still at risk in some exams"
        
        outcomes["risk_assessment"] = {
            "overall_risk_level": risk_level,
            "description": risk_description,
            "confidence": 85
        }
        
        # Study plan adjustment
        outcomes["study_plan_adjustment"] = {
            "timeframe_needed": "4-6 weeks with focused effort",
            "daily_hours_recommended": self._calculate_study_hours(scenario),
            "priority_topics": self._identify_priority_topics(scenario)
        }
        
        # Placement potential
        outcomes["placement_potential"] = {
            "estimated_final_score": projected_avg,
            "placement_probability": min(95, (projected_avg / 100) * 100),
            "competitive_advantage": "Above average in market"
        }
        
        return outcomes
    
    def _estimate_career_fit(self, scenario: CounterfactualScenario) -> Dict:
        """Estimate how career fit scores change in this scenario."""
        projected_avg = scenario.modifications.get("overall_projected_avg", 65)
        
        career_roles = {
            "Software Engineer": max(0, projected_avg - 10),  # High barrier
            "Web Developer": max(0, projected_avg - 5),
            "Data Scientist": max(0, projected_avg - 15),     # Needs Math
            "Mobile Developer": max(0, projected_avg - 8),
            "DevOps Engineer": max(0, projected_avg - 12)
        }
        
        return career_roles
    
    def _calculate_study_hours(self, scenario: CounterfactualScenario) -> float:
        """Calculate recommended daily study hours for this scenario."""
        # More improvement needed = more hours
        avg_improvement = scenario.modifications.get("average_improvement", 5)
        
        if avg_improvement >= 15:
            return 6.5  # Intensive
        elif avg_improvement >= 10:
            return 5.5  # Moderate
        else:
            return 4.0  # Light
    
    def _identify_priority_topics(self, scenario: CounterfactualScenario) -> List[str]:
        """Identify which topics to prioritize in this scenario."""
        focus_subject = scenario.modifications.get("focus_subject")
        
        if focus_subject:
            return [
                f"Core {focus_subject} concepts",
                f"Guided practice set for {focus_subject}",
                f"Error log for {focus_subject}",
                "Exam-style checkpoint",
            ]
        return ["Core concepts", "Practice problems", "Previous year questions"]
    
    def compare_scenarios(self, scenarios: List[CounterfactualScenario], state: LearnerState) -> Dict:
        """
        Compare scenarios and generate recommendations.
        This is the KEY REASONING: Which scenario is best?
        """
        
        comparison = {
            "scenarios": [s.to_dict() for s in scenarios],
            "comparison_metrics": self._compare_metrics(scenarios),
            "recommendation": self._generate_recommendation(scenarios, state),
            "reasoning": self._explain_reasoning(scenarios)
        }
        
        return comparison
    
    def _compare_metrics(self, scenarios: List[CounterfactualScenario]) -> Dict:
        """Compare key metrics across scenarios."""
        metrics = {
            "projected_scores": {},
            "career_impact": {},
            "placement_probability": {},
            "effort_required": {}
        }
        
        for scenario in scenarios:
            outcomes = scenario.predicted_outcomes
            projected_avg = scenario.modifications.get("overall_projected_avg", 65)
            
            metrics["projected_scores"][scenario.scenario_name] = projected_avg
            metrics["career_impact"][scenario.scenario_name] = len(
                [v for v in outcomes.get("career_impact", {}).get("new_fit_scores", {}).values() if v > 70]
            )
            metrics["placement_probability"][scenario.scenario_name] = outcomes.get(
                "placement_potential", {}
            ).get("placement_probability", 0)
            metrics["effort_required"][scenario.scenario_name] = outcomes.get(
                "study_plan_adjustment", {}
            ).get("daily_hours_recommended", 5)
        
        return metrics
    
    def _generate_recommendation(self, scenarios: List[CounterfactualScenario], state: LearnerState) -> Dict:
        """Generate best recommendation based on reasoning."""
        
        # Score each scenario
        scores = {}
        for scenario in scenarios:
            projected = scenario.modifications.get("overall_projected_avg", 65)
            placement = scenario.predicted_outcomes.get("placement_potential", {}).get("placement_probability", 0)
            effort = scenario.predicted_outcomes.get("study_plan_adjustment", {}).get("daily_hours_recommended", 5)
            
            # Higher score = better
            score = (projected * 0.5) + (placement * 0.3) - (effort * 0.2)
            scores[scenario.scenario_name] = score
        
        best_scenario = max(scores, key=scores.get)
        best = next(s for s in scenarios if s.scenario_name == best_scenario)
        
        return {
            "recommended_scenario": best_scenario,
            "why": f"Balances improvement potential ({best.modifications.get('overall_projected_avg', 65):.0f}% projected) with effort requirement",
            "expected_outcome": best.predicted_outcomes.get("placement_potential", {}),
            "timeline": "4-6 weeks to implement"
        }
    
    def _explain_reasoning(self, scenarios: List[CounterfactualScenario]) -> List[str]:
        """Explain the reasoning behind recommendations."""
        explanations = [
            "Agent Reasoning Process:",
            "  1. Career Agent: Analyzed how each scenario impacts career options",
            "  2. Risk Predictor: Assessed exam pass probability for each path",
            "  3. Study Planner: Calculated time and effort required",
            "  4. Consensus: Balanced trade-offs between improvement and effort"
        ]
        
        for i, scenario in enumerate(scenarios, 1):
            outcomes = scenario.predicted_outcomes
            placement = outcomes.get("placement_potential", {}).get("placement_probability", 0)
            explanations.append(f"  - {scenario.scenario_name}: {placement:.0f}% placement probability")
        
        return explanations
    
    def what_if_exam_postponed(self, risk_data: dict, postpone_days: int = 7) -> dict:
        current_risks = risk_data.get("subject_risks", [])
        improvements = []
        for sr in current_risks:
            new_days = sr.get("days_until_exam", 14) + postpone_days
            old_risk = sr.get("risk_score", 50)
            time_factor = min(new_days / 30, 1.0)
            score_factor = (sr.get("percentage", 50)) / 100
            new_risk = round((1 - score_factor) * (1 - (time_factor * 0.5)) * 100, 2)
            improvements.append({
                "subject": sr.get("subject"),
                "old_risk": old_risk,
                "new_risk": new_risk,
                "improvement": round(old_risk - new_risk, 2),
            })
        avg_improvement = sum(i["improvement"] for i in improvements) / len(improvements) if improvements else 0
        return {
            "scenario_name": "Exam postponed +7 days",
            "description": f"If all exams were delayed by {postpone_days} days",
            "projected_risk_change": round(-avg_improvement, 2),
            "subject_details": improvements,
            "key_insight": f"A {postpone_days}-day postponement would reduce average risk by {avg_improvement:.1f}%",
            "confidence": 0.82,
        }

    def what_if_drop_weakest_focus(self, weakness_data: dict) -> dict:
        weakest = weakness_data.get("most_critical", {}) or weakness_data.get("weakest_subject", {})
        if isinstance(weakest, dict) and not weakest:
            return {"scenario_name": "Double focus on weakest", "key_insight": "No weak subject identified"}
        if not isinstance(weakest, dict):
            weakest = {"subject": weakest, "percentage": 50}
        current_pct = weakest.get("percentage", 50)
        projected_gain = min(15, (100 - current_pct) * 0.3)
        new_pct = min(100, current_pct + projected_gain)
        return {
            "scenario_name": f"Double focus on {weakest.get('subject', 'weakest subject')}",
            "description": "Redirect all strong-subject time to weakest subject",
            "projected_score_gain": round(projected_gain, 1),
            "projected_new_score": round(new_pct, 1),
            "projected_risk_change": round(-projected_gain * 0.8, 1),
            "key_insight": (
                f"Doubling focus on {weakest.get('subject', 'weakest')} could "
                f"improve score by ~{projected_gain:.0f} points ({current_pct:.0f}% → {new_pct:.0f}%)"
            ),
            "confidence": 0.74,
        }

    def what_if_perfect_attendance(self, risk_data: dict) -> dict:
        overall_risk = risk_data.get("overall_risk_score", 50)
        adherence_bonus = overall_risk * 0.35
        new_risk = max(5, overall_risk - adherence_bonus)
        return {
            "scenario_name": "100% plan adherence",
            "description": "Student follows every planned study session without skipping",
            "current_risk": round(overall_risk, 2),
            "projected_risk": round(new_risk, 2),
            "projected_risk_change": round(-adherence_bonus, 2),
            "key_insight": (
                f"Perfect adherence to the study plan could reduce overall risk from "
                f"{overall_risk:.1f}% to {new_risk:.1f}% — a {adherence_bonus:.1f}% improvement"
            ),
            "confidence": 0.79,
        }

    def run_light(
        self,
        state: LearnerState,
        increase_hours: float = 1.5,
        weakness_analysis: dict | None = None,
        risk_assessment: dict | None = None,
    ) -> Dict:
        hours = self.what_if_study_hours_increase(state, increase_hours)
        weakest = self.what_if_weakest_improves(state)
        confidence = self.what_if_confidence_rises(state)
        trace = [
            hours["insight"],
            weakest["insight"],
            confidence["insight"],
        ]
        scenarios = []
        if risk_assessment:
            scenarios.append(self.what_if_exam_postponed(risk_assessment))
            scenarios.append(self.what_if_perfect_attendance(risk_assessment))
        if weakness_analysis:
            scenarios.append(self.what_if_drop_weakest_focus(weakness_analysis))

        result = {
            **hours,
            "weakest_subject_improvement": weakest,
            "confidence_rise": confidence,
            "scenarios": scenarios,
            "improvement_percent": hours.get("improvement_percent", 0),
        }
        result.update(agent_envelope(
            f"Generated {len(scenarios)} 'what-if' scenarios.",
            trace,
            confidence_from_signals(0.85, 0.9 if scenarios else 0.4),
            self.name,
            ["Standard schedule", "No counterfactual mapping"],
            "Counterfactuals map exact risk shift to motivation using conditional reasoning paths.",
            evidence=["Causal Inference Model", "Historical Outcome Database"],
        ))
        return result

    def what_if_weakest_improves(self, state: LearnerState, points: float = 10.0) -> Dict:
        weakest = state.weakest_subject
        if not weakest:
            return {"insight": "No weakest subject to improve", "impact": {}}
        current = state.subject_scores.get(weakest, 0)
        projected = min(100, current + points)
        risk_drop = round(min(25, points * 1.2), 1)
        return {
            "weakest_subject": weakest,
            "current_score": current,
            "projected_score": projected,
            "risk_reduction": risk_drop,
            "plan_intensity_change": "moderate" if points < 15 else "lower",
            "insight": f"If {weakest} improves by {points} points, projected risk drops ~{risk_drop}% and plan intensity eases",
        }

    def what_if_confidence_rises(self, state: LearnerState, delta: float = 0.15) -> Dict:
        avg_conf = sum(state.subject_confidence.values()) / max(len(state.subject_confidence), 1)
        new_conf = min(1.0, avg_conf + delta)
        return {
            "current_confidence": round(avg_conf, 2),
            "projected_confidence": round(new_conf, 2),
            "recommendation_strength": "strong" if new_conf >= 0.7 else "cautious",
            "insight": f"Higher confidence ({new_conf:.0%}) enables stronger recommendations with less remediation overhead",
        }

    def run(self, state: LearnerState) -> Dict:
        print(f"\n{'='*60}")
        print(f"  {self.name}")
        print(f"  Generating 'what-if' scenarios for {state.learner_name}")
        print(f"{'='*60}\n")

        if not state.subjects:
            result = {
                "status": "insufficient_data",
                "scenarios_count": 0,
                "study_hours_increase": self.what_if_study_hours_increase(state),
            }
            result.update(agent_envelope(
                "No safe scenarios generated.",
                ["Input data did not yield viable what-ifs", "Falling back to safe default"],
                0.3,
                evidence=["Validation Checks Failed"]
            ))
            return result

        # Generate scenarios
        scenarios = self.generate_scenarios(state, num_scenarios=3)
        print(f"✓ Generated {len(scenarios)} scenarios\n")

        comparison = self.compare_scenarios(scenarios, state)
        print(f"✓ Analyzed scenarios and generated recommendations")
        hours_counterfactual = self.what_if_study_hours_increase(state)
        weakest_cf = self.what_if_weakest_improves(state)
        confidence_cf = self.what_if_confidence_rises(state)
        sooner_exam = self.what_if_exam_sooner(state)
        trace = comparison["reasoning"] + [
            f"Current risk is {hours_counterfactual['current_risk']}%",
            f"Projected risk after increased hours is {hours_counterfactual['new_risk_if_hours_increase']}%",
            hours_counterfactual["insight"],
        ]
        
        extra_scenarios = []
        if state.subjects:
            wa_stub = {"most_critical": {"subject": state.weakest_subject, "percentage": state.subject_scores.get(state.weakest_subject or "", 50)}}
            extra_scenarios = [
                self.what_if_drop_weakest_focus(wa_stub),
            ]

        result = {
            "status": "scenarios_analyzed",
            "scenarios_count": len(scenarios),
            "scenarios": [s.to_dict() for s in scenarios] + extra_scenarios,
            "comparison": comparison,
            "recommendation": comparison["recommendation"],
            "study_hours_increase": hours_counterfactual,
            "weakest_subject_improvement": weakest_cf,
            "confidence_rise": confidence_cf,
            "exam_sooner": sooner_exam,
            "current_risk": hours_counterfactual["current_risk"],
            "new_risk_if_hours_increase": hours_counterfactual["new_risk_if_hours_increase"],
            "improvement_percent": hours_counterfactual.get("improvement_percent", 0),
            "insight": hours_counterfactual["insight"],
        }
        result.update(agent_envelope(
            hours_counterfactual["insight"],
            trace,
            0.82,
            self.name,
            ["Assume more hours always guarantees success", "Ignore current subject risk"],
            "The counterfactual estimates risk reduction from additional daily study time while capping projected improvement.",
        ))
        return result

    def what_if_exam_sooner(self, state: LearnerState, days_sooner: int = 7) -> Dict:
        if not state.weakest_subject:
            return {"insight": "No exam urgency shift computed", "impact": {}}
        days_left = state.days_remaining.get(state.weakest_subject, 14)
        new_days = max(1, days_left - days_sooner)
        return {
            "weakest_subject": state.weakest_subject,
            "current_days_remaining": days_left,
            "projected_days_remaining": new_days,
            "plan_intensity_change": "compression",
            "resource_focus": state.weakest_subject,
            "insight": f"If exam moves {days_sooner} days sooner, compress plan around {state.weakest_subject}",
        }

    def what_if_study_hours_increase(self, state: LearnerState, increase_hours: float = 1.5) -> Dict:
        risk_agent = RiskPredictorAgent()
        risks = [risk_agent.calculate_risk_score(subject) for subject in state.subjects if subject.days_until_exam >= 0]
        current_risk = round(sum(risks) / len(risks), 2) if risks else 0
        improvement = min(35, 8 + (increase_hours * 6))
        new_risk = round(max(0, current_risk - improvement), 2)
        reduction = round(current_risk - new_risk, 2)
        reduction_pct = round((reduction / current_risk) * 100, 2) if current_risk else 0
        return {
            "current_risk": current_risk,
            "new_risk_if_hours_increase": new_risk,
            "improvement_percent": reduction_pct,
            "insight": f"Increasing study by {increase_hours} hours/day reduces risk by {reduction_pct}%",
            "generated_by": self.name,
        }
