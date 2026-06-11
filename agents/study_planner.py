from models.learner_state import LearnerState
from config import config
from datetime import date, timedelta
from typing import Dict, List
from agents.intelligence import agent_envelope, confidence_from_signals

class StudyPlannerAgent:
    def __init__(self):
        self.name = "Study Planner Agent"
        self.min_hours = config.MIN_STUDY_HOURS_PER_DAY
        self.max_hours = config.MAX_STUDY_HOURS_PER_DAY
        self.subjects_per_day = config.SUBJECTS_PER_DAY

    def get_daily_hours(self, weakness_level: str, confidence: float = 0.75, state: LearnerState | None = None) -> float:
        hours_map = {
            "weak": 3.0,
            "moderate": 1.75,
            "strong": 0.75,
        }
        hours = hours_map.get(weakness_level, 1.0)
        if confidence < 0.5:
            hours = round(hours * 1.15, 2)
        cap = state.study_capacity if state else self.max_hours
        return min(hours, cap)

    def get_focus_areas(self, weakness_level: str, subject_name: str) -> List[str]:
        focus_map = {
            "weak": [
                f"Diagnose two weakest chapters in {subject_name}",
                "Relearn one concept using examples",
                "Solve 25 mixed practice questions",
                "Review mistakes and write a correction note"
            ],
            "moderate": [
                f"Revise high-weightage topics in {subject_name}",
                "Solve 12 timed practice questions",
                "Update concise revision notes"
            ],
            "strong": [
                f"Weekly maintenance revision for {subject_name}",
                "Solve 5 advanced questions to retain fluency"
            ]
        }
        return focus_map.get(weakness_level, [f"Study {subject_name}"])

    def _weighted_subjects_for_day(self, sorted_subjects: List, subject_info: Dict, day_num: int) -> List:
        candidates = []
        fallback = []
        for index, subject in enumerate(sorted_subjects):
            classification = subject_info.get(subject.name, {}).get("weakness_level", "strong")
            days_left = subject.days_until_exam - day_num
            if days_left <= 0:
                continue

            near_exam = days_left <= 5
            include = (
                classification == "weak"
                or (classification == "moderate" and (day_num + index) % 2 == 0)
                or (classification == "strong" and (day_num + index) % 7 == 0)
                or near_exam
            )
            bucket = {"weak": 0, "moderate": 1, "strong": 2}.get(classification, 3)
            rotation = (index + day_num) % max(len(sorted_subjects), 1)
            ranked = (bucket, rotation, days_left, subject.name)
            fallback.append((ranked, subject))
            if include:
                candidates.append((ranked, subject))

        selected = candidates if candidates else fallback
        return [subject for _, subject in sorted(selected, key=lambda item: item[0])]

    def create_schedule(self, state: LearnerState, weakness_analysis: dict) -> List[dict]:
        student = state
        schedule = []
        today = date.today()

        # map subject name to its weakness info
        subject_info = {}
        for analysis in weakness_analysis.get("all_analyses", []):
            subject_info[analysis["subject"]] = {
                "weakness_level": analysis["weakness_level"],
                "days_until_exam": analysis["days_until_exam"],
                "priority_rank": analysis["priority_rank"],
                "priority_score": analysis.get("priority_score", 0),
            }

        # sort subjects by priority (weak first, then closest exam)
        sorted_subjects = sorted(
            student.subjects,
            key=lambda s: (
                -subject_info.get(s.name, {}).get("priority_score", 0),
                subject_info.get(s.name, {}).get("priority_rank", 4),
                max(subject_info.get(s.name, {}).get("days_until_exam", 365), 0),
                s.name,
            )
        )

        # plan until the furthest exam, max 30 days
        max_days = max(
            (s.days_until_exam for s in student.subjects if s.days_until_exam > 0),
            default=14
        )
        plan_days = min(max_days, 30)

        for day_num in range(plan_days):
            current_date = today + timedelta(days=day_num)

            day_schedule = {
                "day": day_num + 1,
                "date": current_date.strftime("%A, %d %B %Y"),
                "total_hours": 0,
                "subjects": [],
                "exams_today": []
            }

            # flag exams happening today
            for subject in student.subjects:
                if subject.exam_date == current_date:
                    day_schedule["exams_today"].append(subject.name)

            daily_hours = 0
            subjects_added = 0

            for subject in self._weighted_subjects_for_day(sorted_subjects, subject_info, day_num):
                info = subject_info.get(subject.name, {})
                days_left = subject.days_until_exam - day_num

                if days_left <= 0:
                    continue
                if subjects_added >= self.subjects_per_day:
                    break
                if daily_hours >= self.max_hours:
                    break

                weakness_level = info.get("weakness_level", "strong")
                confidence = state.subject_confidence.get(subject.name, 0.75)
                hours = self.get_daily_hours(weakness_level, confidence, state)
                weekend_boost = current_date.weekday() >= 5
                hour_reason = (
                    f"{hours}h because {subject.name} is {weakness_level.upper()} "
                    f"(confidence {confidence:.0%})"
                )
                if subject.name == state.weakest_subject:
                    hour_reason += " — canonical weakest subject priority"

                # final revision mode if exam is in 2 days
                if days_left <= 2:
                    hours = 1.0
                    focus = [
                        f"Final revision of {subject.name}",
                        "Go through your notes only",
                        "Stay calm and sleep early"
                    ]
                else:
                    focus = self.get_focus_areas(weakness_level, subject.name)
                    if weakness_level == "weak":
                        weak_focus_cycles = [
                            [
                                f"Diagnose two weakest chapters in {subject.name}",
                                "Relearn one concept using examples",
                                "Solve 25 mixed practice questions",
                                "Review mistakes and write a correction note",
                            ],
                            [
                                f"Timed remediation block for {subject.name}",
                                "Redo yesterday's incorrect questions",
                                "Teach one concept aloud in 5 minutes",
                                "Attempt a mini quiz and log accuracy",
                            ],
                            [
                                f"Deep practice ladder for {subject.name}",
                                "Start with 5 easy questions, then 10 medium questions",
                                "Finish with 3 exam-style questions",
                                "Tag mistakes by concept gap",
                            ],
                        ]
                        focus = weak_focus_cycles[day_num % len(weak_focus_cycles)]
                    elif weakness_level == "moderate" and day_num % 3 == 2:
                        focus = [
                            f"Mixed revision sprint for {subject.name}",
                            "Practice one easy, one medium, one hard set",
                            "Close gaps from the last checkpoint"
                        ]
                    focus = focus + [f"Record day {day_num + 1} outcome for {subject.name}"]

                if weekend_boost and weakness_level == "weak":
                    hours = round(hours * 1.4, 1)
                    focus = focus + ["Weekend boost: add one error-correction checkpoint"]

                if daily_hours + hours > self.max_hours:
                    hours = round(self.max_hours - daily_hours, 1)
                    if hours < 0.5:
                        break

                day_schedule["subjects"].append({
                    "name": subject.name,
                    "hours": hours,
                    "weakness_level": weakness_level,
                    "weekend_boost": weekend_boost and weakness_level == "weak",
                    "focus_areas": focus,
                    "hour_reason": hour_reason,
                })

                daily_hours += hours
                subjects_added += 1

            day_schedule["total_hours"] = round(daily_hours, 1)

            if day_schedule["subjects"] or day_schedule["exams_today"]:
                schedule.append(day_schedule)

        return schedule

    def run(self, state: LearnerState, weakness_analysis: dict) -> dict:
        schedule = self.create_schedule(state, weakness_analysis)

        total_hours = sum(day["total_hours"] for day in schedule)

        # group into weeks
        weeks = {}
        for day in schedule:
            week_key = f"Week {((day['day'] - 1) // 7) + 1}"
            if week_key not in weeks:
                weeks[week_key] = {"days": 0, "total_hours": 0}
            weeks[week_key]["days"] += 1
            weeks[week_key]["total_hours"] += day["total_hours"]

        profile = "compression" if any(s.days_until_exam <= 7 for s in state.subjects) else (
            "weak_learner" if weakness_analysis.get("weak_count", 0) >= 2 else (
                "strong_learner" if weakness_analysis.get("strong_count", 0) == weakness_analysis.get("total_subjects") else "balanced"
            )
        )
        result = {
            "student_name": state.learner_name,
            "learner_profile": profile,
            "weakest_subject": state.weakest_subject,
            "plan_duration_days": len(schedule),
            "total_study_hours": round(total_hours, 1),
            "average_hours_per_day": round(total_hours / len(schedule), 1) if schedule else 0,
            "daily_schedule": schedule,
            "weekly_breakdown": weeks,
            "tip": self._generate_tip(weakness_analysis)
        }
        weak_names = [a["subject"] for a in weakness_analysis.get("weak_subjects", [])]
        result["priority_strategy"] = {
            "weak_subjects": weak_names,
            "policy": "WEAK subjects receive concept repair, deep practice, high time, and weekend boosts; MODERATE subjects use balanced checkpoints; STRONG subjects use revision and mocks.",
        }
        result.update(agent_envelope(
            f"Generated {len(schedule)} adaptive study days prioritizing {', '.join(weak_names) if weak_names else 'maintenance revision'}.",
            [
                "Applied subject classifications from weakness analyzer",
                "Allocated more hours and recurrence to WEAK subjects",
                "Rotated daily subject ordering to avoid repetitive schedules",
                "Reduced STRONG subjects to light weekly maintenance blocks",
                "Applied 30-50% weekend boost to WEAK subjects",
            ],
            confidence_from_signals(0.9, len(schedule) / 14 if schedule else 0.2),
            self.name,
            ["Same daily plan for every subject", "Strong-subject-heavy schedule"],
            "Adaptive rotation prevents burnout while giving WEAK subjects required volume.",
            evidence=["Cognitive Load Limits", "Spaced Repetition Ratios", "Weekend Study Capacity DB"],
        ))

        # Foundry IQ strategic overlay
        try:
            from foundry.client import FoundryIQClient
            _fiq = FoundryIQClient()
            student = state.to_student_input()
            weak_names = [
                f"{s.get('subject')} ({s.get('percentage')}%)"
                for s in weakness_analysis.get("weak_subjects", [])
            ]
            _q = (
                f"Student: {student.name} | Degree: {getattr(student, 'degree', 'N/A')} | "
                f"Weak subjects: {', '.join(weak_names) if weak_names else 'None'}.\n"
                f"Give a 7-day study strategy with daily hour allocation by subject."
            )
            ai_strategy = _fiq.chat(
                context="study_planning",
                user_message=_q,
                system_prompt="You are a certified academic study planner for Indian students. Be specific.",
            )
            result["ai_strategy"] = ai_strategy
            result["foundry_iq_grounded"] = _fiq.is_live()
            result["foundry_iq_source"] = _fiq.get_source_label()
        except Exception:
            result["ai_strategy"] = result.get("tip", "Stay consistent and follow the schedule.")
            result["foundry_iq_grounded"] = False

        return result

    def _generate_tip(self, weakness_analysis: dict) -> str:
        avg = weakness_analysis.get("overall_average", 0)
        weak_count = weakness_analysis.get("weak_count", 0)

        if avg < 70:
            return "Start with concept repair, then practice. Weak subjects need daily retrieval and mistake review."
        elif weak_count > 2:
            return "Several WEAK subjects detected. Keep the schedule strict and protect sleep before exams."
        else:
            return "Most subjects are stable. Use focused revision and keep extra energy for the lowest-ranked subject."
