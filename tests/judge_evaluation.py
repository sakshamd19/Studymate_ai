import sys
import json
from pathlib import Path
from datetime import date, timedelta
from typing import Dict, List, Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from agents.orchestrator import OrchestratorAgent
from models.student import StudentInput

def run_pipeline(student: StudentInput) -> Dict:
    report = OrchestratorAgent().run(student, include_advanced_reasoning=True, test_mode=True)
    from dataclasses import asdict
    return json.loads(json.dumps(asdict(report), default=str))

def test_case(scenario: str) -> StudentInput:
    today = date.today()
    if scenario == "normal":
        student = StudentInput("Test Normal", "Science", "school")
        student.add_subject("Mathematics", 50, today + timedelta(days=10), confidence=0.3)
        student.add_subject("Physics", 75, today + timedelta(days=15), confidence=0.8)
        student.add_subject("Chemistry", 90, today + timedelta(days=20), confidence=0.9)
        return student
    elif scenario == "normal_high_confidence":
        student = StudentInput("Test Normal HC", "Science", "school")
        student.add_subject("Mathematics", 50, today + timedelta(days=10), confidence=0.9)
        student.add_subject("Physics", 75, today + timedelta(days=15), confidence=0.8)
        student.add_subject("Chemistry", 90, today + timedelta(days=20), confidence=0.9)
        return student
    elif scenario == "edge":
        student = StudentInput("Test Edge", "Science", "school")
        student.add_subject("Mathematics", 70, today + timedelta(days=10), confidence=0.5)
        student.add_subject("Physics", 70, today + timedelta(days=10), confidence=0.5)
        student.add_subject("Chemistry", 70, today + timedelta(days=10), confidence=0.5)
        return student
    raise ValueError(f"Unknown scenario {scenario}")

def evaluate(report: Dict, student: StudentInput, baseline_report: Dict = None) -> List[str]:
    penalties = []
    
    # Identify weakest subject manually for verification
    if not student.subjects:
        return ["No subjects in input"]
    
    weakest = min(student.subjects, key=lambda s: s.percentage).name
    
    # 1. Weakest subject enforcement
    # Study Plan
    study_plan_str = json.dumps(report.get("study_plan", {}))
    if weakest not in study_plan_str:
        penalties.append(f"Weakest subject '{weakest}' not found in study plan.")
        
    # Risk
    risk_str = json.dumps(report.get("risk_assessment", {}))
    if weakest not in risk_str:
        penalties.append(f"Weakest subject '{weakest}' not found in risk assessment.")
        
    # Resources
    resources_str = json.dumps(report.get("resources", {}))
    if weakest not in resources_str:
        penalties.append(f"Weakest subject '{weakest}' not found in resources.")

    # 2. Confidence sensitivity
    if baseline_report:
        # Check if output differs from baseline
        if json.dumps(report.get("study_plan")) == json.dumps(baseline_report.get("study_plan")) and \
           json.dumps(report.get("risk_assessment")) == json.dumps(baseline_report.get("risk_assessment")):
            penalties.append("Outputs did not differ when confidence was changed.")
            
    # 3. Reasoning presence
    has_reasoning = False
    for k, v in report.items():
        if isinstance(v, dict) and v.get("reasoning_trace"):
            has_reasoning = True
            break
    if not has_reasoning:
        penalties.append("No reasoning_trace found or it was empty.")
        
    # 4. Consensus presence
    consensus = report.get("consensus", {})
    if not consensus:
        penalties.append("Consensus report is missing or empty.")
        
    # 5. Consistency
    consistency = report.get("consistency", {})
    if consistency:
        score = consistency.get("consistency_score")
        if score is not None:
            # Handle out of 1 or out of 100
            val = float(score)
            if (val <= 1.0 and val < 0.7) or (val > 1.0 and val < 70.0):
                penalties.append(f"Consistency score {val} is below 0.7/70.")
                
    return penalties

def run_all_tests():
    print("=" * 60)
    print("BRUTAL JUDGE EVALUATION SYSTEM")
    print("=" * 60)
    
    total_score = 100
    all_penalties = []
    
    try:
        # Normal case
        student_normal = test_case("normal")
        report_normal = run_pipeline(student_normal)
        p1 = evaluate(report_normal, student_normal)
        if p1:
            all_penalties.extend([f"[Normal] {p}" for p in p1])
            
        # Confidence sensitivity test
        student_hc = test_case("normal_high_confidence")
        report_hc = run_pipeline(student_hc)
        p2 = evaluate(report_hc, student_hc, baseline_report=report_normal)
        if p2:
            all_penalties.extend([f"[Conf Sens] {p}" for p in p2])
            
        # Edge case
        student_edge = test_case("edge")
        report_edge = run_pipeline(student_edge)
        p3 = evaluate(report_edge, student_edge)
        if p3:
            all_penalties.extend([f"[Edge] {p}" for p in p3])
            
    except Exception as e:
        all_penalties.append(f"[Fatal] Hard crash during evaluation: {e}")
        
    # Deduct 10 points for each penalty
    final_score = max(0, total_score - (len(all_penalties) * 10))
    
    print("\nRESULTS:\n")
    print(f"Final score: {final_score}/100")
    if all_penalties:
        print("\nPenalties:")
        for p in all_penalties:
            print(f"  - {p}")
    else:
        print("\nPenalties: None")
        
    print("\nInterpretation:")
    if final_score >= 90:
        print("WINNER LEVEL")
    elif final_score >= 80:
        print("FINALIST LEVEL")
    elif final_score >= 70:
        print("GOOD BUT BREAKABLE")
    else:
        print("REJECTED")
        
if __name__ == "__main__":
    run_all_tests()
