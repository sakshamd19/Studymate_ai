from dataclasses import asdict
import time

from models.student import StudentInput, AgentReport
from models.learner_state import LearnerState
from config import config
from agents.intelligence import FAILSAFE_MESSAGE, agent_envelope, serializable_report, validate_student_input
from agents.input_normalizer import normalize_student_input
from agents.consistency_validator import ConsistencyValidator


class OrchestratorAgent:
    def __init__(self):
        self.name = "Orchestrator Agent"

    def run(self, student: StudentInput, include_mock_exam: bool = False, include_advanced_reasoning: bool = False, test_mode: bool = False) -> AgentReport:
        student = normalize_student_input(student)
        print(f"\n{'='*50}")
        print(f"  {config.APP_NAME} — Starting Analysis")
        print(f"  Student: {student.name} | Stream: {student.stream}")
        print(f"{'='*50}\n")

        report = AgentReport()
        execution_chain = []
        safety = validate_student_input(student)
        report.safety_status = safety
        if not safety["is_valid"]:
            safe_payload = agent_envelope(
                FAILSAFE_MESSAGE,
                ["Input validation failed", *safety["issues"], "Stopped pipeline to avoid hallucination or unsafe use of data"],
                0.2,
                self.name,
                ["Generate a partial plan from unsafe input"],
                "The input failed synthetic-data or sufficiency validation.",
            )
            report.weakness_analysis = safe_payload
            report.study_plan = safe_payload
            report.risk_assessment = safe_payload
            report.resources = safe_payload
            report.career_readiness = safe_payload
            report.observability = {
                "agent_execution_chain": execution_chain,
                "latency_per_agent_ms": {},
                "stopped_early": True,
            }
            return report

        import concurrent.futures
        import threading
        
        state = LearnerState.from_student(student, test_mode=test_mode)
        report.learner_state = asdict(state) if hasattr(state, "__dataclass_fields__") else {}

        chain_lock = threading.Lock()
        def timed(agent_name, fn, *args, **kwargs):
            started = time.perf_counter()
            output = fn(*args, **kwargs)
            latency = round((time.perf_counter() - started) * 1000, 2)
            with chain_lock:
                execution_chain.append({"agent": agent_name, "latency_ms": latency})
            return output

        from agents.weakness_analyzer import WeaknessAnalyzerAgent
        from agents.study_planner import StudyPlannerAgent
        from agents.risk_predictor import RiskPredictorAgent
        from agents.resource_finder import ResourceFinderAgent
        from agents.consensus_mediator import ConsensusMediator
        from agents.counterfactual_reasoner import CounterfactualReasoner
        from agents.career_readiness import CareerReadinessAgent
        from agents.critic_agent import CriticAgent
        from evaluation.evaluator import EvaluationAgent
        from agents.learning_path_curator import LearningPathCurator
        from agents.engagement_agent import EngagementAgent
        from agents.assessment_agent import AssessmentAgent
        from agents.manager_insights_agent import ManagerInsightsAgent

        weakness_agent = WeaknessAnalyzerAgent()
        planner_agent = StudyPlannerAgent()
        risk_agent = RiskPredictorAgent()
        resource_agent = ResourceFinderAgent()
        career_agent = CareerReadinessAgent()
        reasoner = CounterfactualReasoner()
        critic = CriticAgent()
        validator = ConsistencyValidator()
        evaluator = EvaluationAgent()
        mediator = ConsensusMediator()
        curator = LearningPathCurator()
        engagement = EngagementAgent()
        assessment = AssessmentAgent()
        manager = ManagerInsightsAgent()

        print("Phase 2: Generate learning path (Curator, WeaknessAnalyzer, ResourceFinder)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
            future_weakness = executor.submit(timed, weakness_agent.name, weakness_agent.run, state)
            future_curator = executor.submit(timed, curator.name, curator.run, state)
            
            report.weakness_analysis = future_weakness.result()
            report.learning_path = future_curator.result()
            
            future_resource = executor.submit(timed, resource_agent.name, resource_agent.run, state, report.weakness_analysis)
            report.resources = future_resource.result()
            report.foundry_iq = report.resources.get("synthetic_iq", {})

        print("Phase 3: Convert to study schedule (StudyPlanner, Counterfactual)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_planner = executor.submit(timed, planner_agent.name, planner_agent.run, state, report.weakness_analysis)
            report.study_plan = future_planner.result()
            
            if not include_advanced_reasoning:
                future_counter_light = executor.submit(timed, reasoner.name, reasoner.run_light, state, weakness_analysis=report.weakness_analysis, risk_assessment={})
                report.counterfactuals = future_counter_light.result()
            else:
                future_counter = executor.submit(timed, reasoner.name, reasoner.run, state)
                report.counterfactuals = future_counter.result()

        print("Phase 4: Track engagement (EngagementAgent, RiskPredictor)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_risk = executor.submit(timed, risk_agent.name, risk_agent.run, state)
            future_eng = executor.submit(timed, engagement.name, engagement.run, state)
            
            report.risk_assessment = future_risk.result()
            report.engagement_tracking = future_eng.result()

        print("Phase 5: Assess readiness (AssessmentAgent, CareerReadiness)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
            future_assess = executor.submit(timed, assessment.name, assessment.run, state)
            future_career = executor.submit(timed, career_agent.name, career_agent.run, state)
            
            report.assessment = future_assess.result()
            report.career_readiness = future_career.result()

        print("Phase 6: Recommend next step (ManagerInsights, Evaluation & Consensus)...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            future_manager = executor.submit(timed, manager.name, manager.run, state)
            future_critic = executor.submit(timed, critic.name, critic.run, report, state)
            future_validator = executor.submit(timed, validator.name, validator.run, state, serializable_report(report))
            future_consensus = executor.submit(timed, "Consensus Mediator", mediator.generate_full_consensus_report, asdict(report), state)
            
            report.manager_insights = future_manager.result()
            report.critic_review = future_critic.result()
            report.consistency = future_validator.result()
            report.consensus = future_consensus.result()
        
        report.observability = {
            "agent_execution_chain": execution_chain,
            "latency_per_agent_ms": {entry["agent"]: entry["latency_ms"] for entry in execution_chain},
            "stopped_early": False,
            "weakest_subject_priority": state.weakest_subject,
        }
        
        report.evaluation = timed(evaluator.name, evaluator.run, serializable_report(report), execution_chain, state)
        
        # Update observability with evaluator runtime
        report.observability["agent_execution_chain"] = execution_chain
        report.observability["latency_per_agent_ms"] = {entry["agent"]: entry["latency_ms"] for entry in execution_chain}

        print(f"{'='*50}")
        print(f"  Analysis Complete for {student.name}!")
        print(f"{'='*50}\n")
        return report
