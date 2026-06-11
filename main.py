from models.student import StudentInput
from agents.orchestrator import OrchestratorAgent
from datetime import date, timedelta

def create_sample_student() -> StudentInput:
    student = StudentInput(
        name="L-1001",
        stream="TECH",
        learner_level="university",
        degree_group="TECH",
        degree="BTech / BE",
        specialization="Software Engineering",
    )

    today = date.today()

    student.add_subject("Mathematics",      score=45, exam_date=today + timedelta(days=20))
    student.add_subject("Physics",          score=38, exam_date=today + timedelta(days=15))
    student.add_subject("Chemistry",        score=62, exam_date=today + timedelta(days=18))
    student.add_subject("Computer Science", score=78, exam_date=today + timedelta(days=25))
    student.add_subject("English",          score=55, exam_date=today + timedelta(days=12))

    return student

def print_report(report, student):
    print("\n" + "="*60)
    print("          STUDYMATE AI — FULL REPORT")
    print("="*60)

    # weakness analysis
    wa = report.weakness_analysis
    print(f"\n WEAKNESS ANALYSIS")
    print(f"  Overall Average : {wa['overall_average']}%")
    print(f"  Weak Subjects   : {wa['weak_count']}")
    print(f"  Summary         : {wa['summary']}")
    print(f"\n  Subject Breakdown:")
    for a in wa["all_analyses"]:
        bar = "🔴" if a["weakness_level"] == "weak" else \
              "🟡" if a["weakness_level"] == "moderate" else "🟢"
        print(f"  {bar} {a['subject']:<20} {a['percentage']}%  [{a['weakness_level'].upper()}]  — {a['days_until_exam']} days left")

    # risk assessment
    print(f"\n RISK ASSESSMENT")
    ra = report.risk_assessment
    print(f"  Overall Risk    : {ra['overall_risk_score']}%")
    print(f"  Overall Confidence: {ra['overall_confidence']}%")
    print(f"  Verdict         : {ra['overall_verdict']}")
    if ra["most_at_risk"]:
        print(f"  Most At Risk    : {ra['most_at_risk']['subject']} ({ra['most_at_risk']['risk_level'].upper()})")
    print(f"\n  Subject Risks:")
    for s in ra["subject_risks"]:
        print(f"  • {s['subject']:<20} Risk: {s['risk_score']}%  Confidence: {s['confidence_score']}%")
        print(f"    → {s['prediction']}")

    # study plan
    print(f"\n STUDY PLAN")
    sp = report.study_plan
    print(f"  Duration        : {sp['plan_duration_days']} days")
    print(f"  Total Hours     : {sp['total_study_hours']} hours")
    print(f"  Avg Per Day     : {sp['average_hours_per_day']} hours")
    print(f"  Tip             : {sp['tip']}")
    print(f"\n  First 5 Days Preview:")
    for day in sp["daily_schedule"][:5]:
        print(f"\n  Day {day['day']} — {day['date']}")
        if day["exams_today"]:
            print(f"  ⚠️  EXAM TODAY: {', '.join(day['exams_today'])}")
        for sub in day["subjects"]:
            print(f"  • {sub['name']:<20} {sub['hours']} hrs")

    # resources
    print(f"\n STUDY RESOURCES")
    res = report.resources
    print(f"  Subjects Covered: {res['total_subjects']}")
    for sr in res.get("weak_resources", res.get("subject_resources", []))[:2]:
        print(f"\n  {sr['subject']} [{sr.get('weakness_level', 'n/a').upper()}]")
        if sr.get("tip"):
            print(f"  Tip: {sr['tip']}")
        print("  Curated resources:")
        for item in sr.get("curated_resources", [])[:3]:
            print(f"   • {item['title']} — {item['url']}")

    # career readiness
    print(f"\n CAREER READINESS")
    cr = report.career_readiness
    print(f"  Detected Stream : {cr['detected_stream'].title()}")
    print(f"  Free Certs Found: {cr['free_cert_count']}")
    top = cr["top_recommended_path"]
    print(f"\n  Top Career Path : {top['title']}")
    print(f"  Avg Salary      : {top['avg_salary']}")
    print(f"  Demand          : {top['demand']}")
    print(f"  Roadmap         : {top['roadmap']}")
    print(f"\n  Skills to Build:")
    for skill in top["skills_needed"][:3]:
        print(f"  • {skill}")
    print(f"\n  Free Certifications to Start Now:")
    for cert in cr["free_certifications"][:3]:
        print(f"  • {cert['name']} — {cert['platform']} ({cert['duration']})")
        print(f"    {cert['url']}")
    print(f"\n  Score Based Advice:")
    for advice in cr["score_based_advice"][:2]:
        print(f"  • {advice}")
    print(f"\n  Immediate Actions:")
    for action in cr["immediate_actions"][:3]:
        print(f"  ✅ {action}")

    print(f"\n EVALUATION")
    ev = report.evaluation
    print(f"  Overall Score      : {ev.get('overall_score')}/{ev.get('max_score', 100)}")
    print(f"  Consistency Score  : {ev.get('consistency_score')}")
    print(f"  Personalization    : {ev.get('personalization_score')}")
    if report.consistency:
        print(f"  Agent Consistency  : {report.consistency.get('consistency_score')}%")

    print("\n" + "="*60)
    print("  Analysis complete! Run app.py for the full UI.")
    print("="*60 + "\n")

def main():
    print("\nStarting StudyMate AI...")
    print("Using synthetic demo learner data only.")
    student = create_sample_student()
    orchestrator = OrchestratorAgent()
    report = orchestrator.run(student)
    print_report(report, student)

if __name__ == "__main__":
    main()
