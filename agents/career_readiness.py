from models.learner_state import LearnerState
from config import config
from typing import Dict, List
from agents.intelligence import FAILSAFE_MESSAGE, agent_envelope, classify_subject, confidence_from_signals

class CareerReadinessAgent:
    def __init__(self):
        self.name = "Career Readiness Agent"
        self.degree_hierarchy = {
            "school_streams": ["Science", "Commerce", "Humanities"],
            "university": {
                "TECH": {
                    "BTech / BE": ["Artificial Intelligence", "Data Science", "Cybersecurity", "Software Engineering"],
                    "BCA": ["Software Development", "Data Analytics", "Cloud Computing"],
                    "BSc Computer Science": ["Artificial Intelligence", "Data Science", "Systems"],
                },
                "BUSINESS": {
                    "BBA": ["Marketing", "Finance", "HR"],
                    "BCom": ["Accounting", "Finance", "Taxation"],
                    "Economics": ["Econometrics", "Policy", "Finance"],
                },
                "LAW": {
                    "LLB": ["Corporate Law", "Criminal Law", "IP Law"],
                    "BA LLB": ["Constitutional Law", "Policy", "Human Rights"],
                },
                "CREATIVE": {
                    "Design": ["UX Design", "Product Design", "Visual Communication"],
                    "Architecture": ["Urban Design", "Sustainable Architecture"],
                },
                "MEDICAL": {
                    "MBBS": ["General Medicine", "Public Health"],
                    "BDS": ["Dental Surgery", "Orthodontics"],
                },
            },
        }
        # mock career database
        # replace with Foundry IQ calls when live grounding is configured
        self.career_db = {
            "science": {
                "career_paths": [
                    {
                        "title": "Software Engineer",
                        "avg_salary": "₹6-25 LPA",
                        "demand": "Very High",
                        "skills_needed": [
                            "Python or Java programming",
                            "Data Structures and Algorithms",
                            "Web Development basics",
                            "Git and GitHub",
                            "Problem solving"
                        ],
                        "certifications": [
                            {"name": "Google IT Support Certificate", "platform": "Coursera", "url": "https://coursera.org/google-certificates/it-support", "duration": "6 months", "cost": "Free with financial aid"},
                            {"name": "Python for Everybody", "platform": "Coursera", "url": "https://coursera.org/specializations/python", "duration": "3 months", "cost": "Free to audit"},
                            {"name": "Meta Front-End Developer", "platform": "Coursera", "url": "https://coursera.org/meta-front-end-developer", "duration": "7 months", "cost": "Free with financial aid"},
                        ],
                        "top_companies": ["Google", "Microsoft", "Amazon", "Flipkart", "Infosys", "TCS"],
                        "roadmap": "Start with Python → DSA → Build projects → Internship → Placement"
                    },
                    {
                        "title": "Data Scientist",
                        "avg_salary": "₹8-30 LPA",
                        "demand": "High",
                        "skills_needed": [
                            "Python and R programming",
                            "Machine Learning basics",
                            "Statistics and Mathematics",
                            "SQL and databases",
                            "Data visualization"
                        ],
                        "certifications": [
                            {"name": "IBM Data Science Certificate", "platform": "Coursera", "url": "https://coursera.org/ibm-data-science", "duration": "4 months", "cost": "Free to audit"},
                            {"name": "Google Data Analytics", "platform": "Coursera", "url": "https://coursera.org/google-data-analytics", "duration": "6 months", "cost": "Free with financial aid"},
                            {"name": "Deep Learning Specialization", "platform": "Coursera", "url": "https://coursera.org/specializations/deep-learning", "duration": "5 months", "cost": "Free to audit"},
                        ],
                        "top_companies": ["Amazon", "Flipkart", "Ola", "Zomato", "Paytm", "IBM"],
                        "roadmap": "Statistics → Python → ML algorithms → Projects → Kaggle competitions → Jobs"
                    },
                    {
                        "title": "Doctor (MBBS)",
                        "avg_salary": "₹8-50 LPA",
                        "demand": "Always High",
                        "skills_needed": [
                            "Strong Biology and Chemistry foundation",
                            "NEET preparation",
                            "Problem solving and patience",
                            "Communication skills"
                        ],
                        "certifications": [
                            {"name": "NEET Preparation Course", "platform": "Unacademy", "url": "https://unacademy.com/goal/neet-ug", "duration": "1-2 years", "cost": "Varies"},
                            {"name": "Basic Life Support (BLS)", "platform": "Red Cross", "url": "https://redcross.org", "duration": "1 day", "cost": "Paid"},
                        ],
                        "top_companies": ["AIIMS", "Private Hospitals", "Government Health Services"],
                        "roadmap": "Clear NEET → MBBS 5.5 years → MD/MS specialization → Practice"
                    }
                ],
                "general_skills": [
                    "Critical thinking and problem solving",
                    "Communication and presentation",
                    "MS Office and Google Workspace",
                    "Basic programming literacy",
                    "English proficiency"
                ],
                "immediate_actions": [
                    "Create a LinkedIn profile and keep it updated",
                    "Start one online course from Coursera or edX this week",
                    "Build a GitHub profile and push any project",
                    "Join coding communities like CodeChef or HackerRank",
                    "Attend college technical fests and hackathons"
                ]
            },
            "commerce": {
                "career_paths": [
                    {
                        "title": "Chartered Accountant (CA)",
                        "avg_salary": "₹7-40 LPA",
                        "demand": "High",
                        "skills_needed": [
                            "Accounting and taxation",
                            "Financial analysis",
                            "Auditing principles",
                            "Business law",
                            "MS Excel advanced"
                        ],
                        "certifications": [
                            {"name": "CA Foundation", "platform": "ICAI", "url": "https://icai.org", "duration": "4 months", "cost": "₹9,800"},
                            {"name": "Excel for Accountants", "platform": "Coursera", "url": "https://coursera.org", "duration": "1 month", "cost": "Free to audit"},
                            {"name": "GST Certification", "platform": "NACIN", "url": "https://nacin.gov.in", "duration": "2 weeks", "cost": "Free"},
                        ],
                        "top_companies": ["Deloitte", "PwC", "KPMG", "EY", "Grant Thornton"],
                        "roadmap": "Commerce board → CA Foundation → CA Intermediate → Articleship → CA Final"
                    },
                    {
                        "title": "Investment Banker / Finance Analyst",
                        "avg_salary": "₹8-50 LPA",
                        "demand": "High",
                        "skills_needed": [
                            "Financial modeling",
                            "Valuation techniques",
                            "Excel and PowerPoint",
                            "Economics understanding",
                            "Analytical thinking"
                        ],
                        "certifications": [
                            {"name": "CFA Level 1", "platform": "CFA Institute", "url": "https://cfainstitute.org", "duration": "6 months", "cost": "Paid"},
                            {"name": "Financial Markets (Yale)", "platform": "Coursera", "url": "https://coursera.org/learn/financial-markets-global", "duration": "7 weeks", "cost": "Free to audit"},
                            {"name": "Investment Banking Course", "platform": "Wall Street Prep", "url": "https://wallstreetprep.com", "duration": "3 months", "cost": "Paid"},
                        ],
                        "top_companies": ["Goldman Sachs", "JP Morgan", "Morgan Stanley", "HDFC", "ICICI"],
                        "roadmap": "Commerce → BBA/BCom → MBA Finance → CFA → Investment Banking"
                    },
                    {
                        "title": "Digital Marketing Manager",
                        "avg_salary": "₹4-20 LPA",
                        "demand": "Very High",
                        "skills_needed": [
                            "SEO and SEM",
                            "Social media marketing",
                            "Content creation",
                            "Google Analytics",
                            "Email marketing"
                        ],
                        "certifications": [
                            {"name": "Google Digital Marketing", "platform": "Google", "url": "https://skillshop.google.com", "duration": "40 hours", "cost": "Free"},
                            {"name": "HubSpot Marketing", "platform": "HubSpot Academy", "url": "https://academy.hubspot.com", "duration": "5 hours", "cost": "Free"},
                            {"name": "Meta Social Media Marketing", "platform": "Coursera", "url": "https://coursera.org/meta-social-media-marketing", "duration": "7 months", "cost": "Free with financial aid"},
                        ],
                        "top_companies": ["Startups", "E-commerce companies", "Marketing agencies", "MNCs"],
                        "roadmap": "Learn basics → Google + HubSpot certifications → Build portfolio → Freelance → Full time"
                    }
                ],
                "general_skills": [
                    "Financial literacy and accounting basics",
                    "MS Excel (advanced level)",
                    "Business communication",
                    "Tally ERP or QuickBooks",
                    "English proficiency"
                ],
                "immediate_actions": [
                    "Get Google's free digital marketing certification",
                    "Learn Excel to an advanced level — it is used everywhere in commerce",
                    "Start reading Economic Times or Business Standard daily",
                    "Create a LinkedIn profile and connect with professionals",
                    "Explore CA Foundation or BBA entrance preparations"
                ]
            },
            "arts": {
                "career_paths": [
                    {
                        "title": "Civil Services Officer (IAS/IPS)",
                        "avg_salary": "₹8-20 LPA + perks",
                        "demand": "Stable",
                        "skills_needed": [
                            "Current affairs awareness",
                            "Essay writing",
                            "General studies knowledge",
                            "Analytical thinking",
                            "Leadership and communication"
                        ],
                        "certifications": [
                            {"name": "UPSC Preparation Course", "platform": "Unacademy", "url": "https://unacademy.com/goal/upsc-civil-services-ias-exam", "duration": "1-2 years", "cost": "Varies"},
                            {"name": "Indian Polity Course", "platform": "ClearIAS", "url": "https://clearias.com", "duration": "Self paced", "cost": "Free"},
                        ],
                        "top_companies": ["Government of India", "State Governments", "PSUs"],
                        "roadmap": "Arts graduation → Optional coaching → UPSC Prelims → Mains → Interview"
                    },
                    {
                        "title": "Journalist / Content Creator",
                        "avg_salary": "₹3-15 LPA",
                        "demand": "Growing",
                        "skills_needed": [
                            "Strong writing skills",
                            "Research and fact checking",
                            "Video editing basics",
                            "Social media literacy",
                            "Communication skills"
                        ],
                        "certifications": [
                            {"name": "Digital Journalism", "platform": "Knight Center", "url": "https://journalismcourses.org", "duration": "4 weeks", "cost": "Free"},
                            {"name": "Content Marketing", "platform": "HubSpot", "url": "https://academy.hubspot.com/courses/content-marketing", "duration": "6 hours", "cost": "Free"},
                        ],
                        "top_companies": ["NDTV", "Times of India", "The Hindu", "YouTube", "Startups"],
                        "roadmap": "Build writing skills → Start a blog → Internship → Entry level journalism → Growth"
                    },
                    {
                        "title": "Psychologist / Counselor",
                        "avg_salary": "₹4-15 LPA",
                        "demand": "Growing Fast",
                        "skills_needed": [
                            "Empathy and listening skills",
                            "Psychology fundamentals",
                            "Communication and counseling",
                            "Research methods",
                            "Ethics in mental health"
                        ],
                        "certifications": [
                            {"name": "Introduction to Psychology (Yale)", "platform": "Coursera", "url": "https://coursera.org/learn/introduction-psychology", "duration": "6 weeks", "cost": "Free to audit"},
                            {"name": "Positive Psychology", "platform": "Coursera", "url": "https://coursera.org/specializations/positivepsychology", "duration": "5 months", "cost": "Free to audit"},
                        ],
                        "top_companies": ["Hospitals", "NGOs", "Schools", "Corporate HR", "Private Practice"],
                        "roadmap": "BA Psychology → MA Psychology → RCI Registration → Practice"
                    }
                ],
                "general_skills": [
                    "Strong written and verbal communication",
                    "Research and analytical skills",
                    "Digital literacy",
                    "Critical thinking",
                    "Creative problem solving"
                ],
                "immediate_actions": [
                    "Start a blog or creative writing portfolio",
                    "Read newspapers daily and stay updated on current affairs",
                    "Join debate clubs or public speaking groups",
                    "Explore free courses on Coursera or edX",
                    "Build a LinkedIn profile showcasing your writing or creative work"
                ]
            },
            "computer science": {
                "career_paths": [
                    {
                        "title": "Full Stack Developer",
                        "avg_salary": "₹5-30 LPA",
                        "demand": "Very High",
                        "skills_needed": [
                            "HTML CSS JavaScript",
                            "React or Angular frontend",
                            "Node.js or Python backend",
                            "SQL and NoSQL databases",
                            "REST APIs and Git"
                        ],
                        "certifications": [
                            {"name": "Full Stack Web Development", "platform": "The Odin Project", "url": "https://theodinproject.com", "duration": "Self paced", "cost": "Free"},
                            {"name": "Meta Full Stack Developer", "platform": "Coursera", "url": "https://coursera.org/meta-back-end-developer", "duration": "9 months", "cost": "Free with financial aid"},
                            {"name": "AWS Cloud Practitioner", "platform": "AWS", "url": "https://aws.amazon.com/certification", "duration": "3 months", "cost": "Paid exam, free prep"},
                        ],
                        "top_companies": ["Google", "Microsoft", "Amazon", "Startups", "Freelance"],
                        "roadmap": "HTML/CSS/JS → React → Backend → Database → Projects → Jobs"
                    },
                    {
                        "title": "AI / ML Engineer",
                        "avg_salary": "₹10-50 LPA",
                        "demand": "Extremely High",
                        "skills_needed": [
                            "Python and libraries (NumPy, Pandas)",
                            "Machine Learning algorithms",
                            "Deep Learning and Neural Networks",
                            "Mathematics and Statistics",
                            "Cloud platforms (AWS, Azure, GCP)"
                        ],
                        "certifications": [
                            {"name": "Machine Learning Specialization", "platform": "Coursera", "url": "https://coursera.org/specializations/machine-learning-introduction", "duration": "3 months", "cost": "Free to audit"},
                            {"name": "TensorFlow Developer Certificate", "platform": "Google", "url": "https://tensorflow.org/certificate", "duration": "3-6 months", "cost": "Paid exam"},
                            {"name": "Azure AI Fundamentals", "platform": "Microsoft", "url": "https://learn.microsoft.com/azure/ai", "duration": "1 month", "cost": "Free learning, paid exam"},
                        ],
                        "top_companies": ["Microsoft", "Google", "OpenAI", "Amazon", "Anthropic", "Meta"],
                        "roadmap": "Python → ML basics → Deep Learning → Projects → Research or Industry"
                    },
                    {
                        "title": "Cybersecurity Analyst",
                        "avg_salary": "₹6-25 LPA",
                        "demand": "Very High",
                        "skills_needed": [
                            "Networking fundamentals",
                            "Linux and scripting",
                            "Ethical hacking basics",
                            "Security frameworks",
                            "Cloud security"
                        ],
                        "certifications": [
                            {"name": "Google Cybersecurity Certificate", "platform": "Coursera", "url": "https://coursera.org/google-cybersecurity", "duration": "6 months", "cost": "Free with financial aid"},
                            {"name": "CompTIA Security+", "platform": "CompTIA", "url": "https://comptia.org/certifications/security", "duration": "3 months", "cost": "Paid exam"},
                            {"name": "CEH (Ethical Hacking)", "platform": "EC-Council", "url": "https://eccouncil.org/train-certify/certified-ethical-hacker-ceh", "duration": "6 months", "cost": "Paid"},
                        ],
                        "top_companies": ["IBM", "Cisco", "Palo Alto Networks", "Banks", "Government"],
                        "roadmap": "Networking → Linux → Python → Ethical Hacking → Certifications → Jobs"
                    }
                ],
                "general_skills": [
                    "Strong programming foundation",
                    "Problem solving and DSA",
                    "Git and version control",
                    "Communication and teamwork",
                    "Cloud basics (AWS or Azure)"
                ],
                "immediate_actions": [
                    "Build and push 2-3 projects to GitHub right now",
                    "Start solving DSA problems on LeetCode daily",
                    "Get one free Google or Microsoft certification",
                    "Contribute to an open source project",
                    "Participate in hackathons — like this one!"
                ]
            }
        }

    def detect_stream(self, state: LearnerState) -> str:
        if state.degree_group == "TECH" or state.degree in {"BTech / BE", "BCA", "BSc Computer Science"}:
            return "computer science"
        if state.degree_group == "BUSINESS":
            return "commerce"
        if state.degree_group in {"LAW", "CREATIVE"}:
            return "arts"
        if state.degree_group == "MEDICAL":
            return "science"

        stream = state.stream.lower().strip()
        subject_names = [s.name.lower() for s in state.subjects]

        if any(k in stream for k in ["cs", "computer", "it", "tech"]):
            return "computer science"
        elif any(k in stream for k in ["science", "pcm", "pcb", "medical", "engineering"]):
            return "science"
        elif any(k in stream for k in ["commerce", "business", "accounts"]):
            return "commerce"
        elif any(k in stream for k in ["arts", "humanities", "social"]):
            return "arts"

        # detect from subjects if stream not clear
        if any(k in subject_names for k in ["computer science", "programming", "cs"]):
            return "computer science"
        elif any(k in subject_names for k in ["physics", "chemistry", "mathematics", "biology"]):
            return "science"
        elif any(k in subject_names for k in ["accountancy", "economics", "business"]):
            return "commerce"
        else:
            return "science"

    def structured_personalization(self, state: LearnerState, weakest_subject: str | None) -> Dict:
        level = state.learner_level.lower()
        interest = (state.interest or "").strip()
        degree_group = (state.degree_group or "").upper()
        degree = state.degree or ""
        specialization = state.specialization or ""
        warnings = []
        reasoning = []

        math_low = any(
            s.name.lower() in {"math", "maths", "mathematics"} and s.percentage < 60
            for s in state.subjects
        )
        if specialization.lower() in {"artificial intelligence", "ai"} and math_low:
            warnings.append("AI specialization selected while mathematics is WEAK; strengthen algebra, probability, and calculus before advanced AI.")
            reasoning.append("Detected AI specialization and low mathematics score")
        if interest.lower() in {"ai", "artificial intelligence"}:
            degree_group = degree_group or "TECH"
            reasoning.append("AI interest prioritizes TECH degrees and AI/Data Science specializations")

        if level in {"school", "cbse"}:
            return {
                "level": level,
                "available_streams": self.degree_hierarchy["school_streams"],
                "reasoning": reasoning or ["School learners receive stream choices only"],
                "warnings": warnings,
            }

        groups = self.degree_hierarchy["university"]
        selected_group = groups.get(degree_group, groups["TECH"] if interest.lower() in {"ai", "artificial intelligence"} else {})
        selected_degree = selected_group.get(degree, {}) if isinstance(selected_group, dict) else {}
        return {
            "level": level,
            "degree_groups": list(groups.keys()),
            "selected_degree_group": degree_group if degree_group in groups else ("TECH" if interest.lower() in {"ai", "artificial intelligence"} else ""),
            "degrees": list(selected_group.keys()) if isinstance(selected_group, dict) else [],
            "selected_degree": degree,
            "specializations": selected_group.get(degree, []) if isinstance(selected_group, dict) and degree else [],
            "selected_specialization": specialization,
            "weakest_subject": weakest_subject,
            "reasoning": reasoning or ["University learners receive group, degree, and specialization options"],
            "warnings": warnings,
        }

    def career_summary(self, state: LearnerState, career_paths: List[Dict], avg_score: float, weakest_subject: str | None) -> Dict:
        interest = (state.interest or "").lower()
        specialization = (state.specialization or "").lower()
        skill_maturity = sum(state.skill_profile.values()) / max(len(state.skill_profile), 1)
        scored_paths = []
        for path in career_paths:
            title = path["title"]
            title_l = title.lower()
            score = avg_score * 0.5 + skill_maturity * 50
            if state.degree_group == "TECH" and any(k in title_l for k in ["software", "ai", "data", "cyber"]):
                score += 10
            if "ai" in interest or "artificial intelligence" in specialization:
                if any(k in title_l for k in ["ai", "data scientist", "software"]):
                    score += 12
            if weakest_subject and weakest_subject.lower() in {"mathematics", "math", "maths"} and any(k in title_l for k in ["ai", "data scientist"]):
                score -= 15
            avg_conf = sum(state.subject_confidence.values()) / max(len(state.subject_confidence), 1)
            if avg_conf < 0.55:
                score -= 8
            scored_paths.append((max(0, min(100, score)), path))

        match, top = max(scored_paths, key=lambda item: item[0]) if scored_paths else (0, {"title": "Academic Recovery"})
        missing = []
        if weakest_subject:
            missing.append(f"Improve {weakest_subject} foundation")
        if any(k in top["title"].lower() for k in ["software", "ai", "data"]):
            missing.extend(["Portfolio project", "Programming practice"])
        return {
            "career": top["title"],
            "match": f"{round(match)}%",
            "career_match_score": round(match, 1),
            "missing_skills": missing[:4],
            "next_step": top.get("roadmap", "Build a synthetic learner portfolio and retest in 2 weeks"),
            "why_this_path": (
                f"Fit reflects degree ({state.degree or 'stream'}), specialization ({state.specialization or 'general'}), "
                f"skill maturity, and weakest subject ({weakest_subject or 'none'})."
            ),
        }
    def get_score_based_advice(self, state: LearnerState) -> List[str]:
        avg = sum(s.percentage for s in state.subjects) / len(state.subjects)
        advice = []

        if avg >= 80:
            advice = [
                "Your scores make you eligible for top tier colleges — target IITs, NITs, or DU",
                "Consider applying for national scholarships like KVPY or NSP",
                "Start preparing for entrance exams like JEE, NEET, or CUET now",
                "Reach out to professors for research internship opportunities"
            ]
        elif avg >= 70:
            advice = [
                "Good scores — focus on maintaining consistency till final exams",
                "Explore state level entrance exams alongside national ones",
                "Start building your skill portfolio with online certifications",
                "Look for summer internships or part-time project work"
            ]
        elif avg >= 60:
            advice = [
                "Scores are average — focus on bringing them up before boards",
                "Private colleges and deemed universities are strong options",
                "Skill-based certifications can compensate for average scores",
                "Consider diploma programs or vocational courses alongside degree"
            ]
        else:
            advice = [
                "Focus fully on improving board scores right now",
                "Many successful careers don't depend on board marks alone",
                "Skill-based learning is your strongest asset — start certifications",
                "Explore vocational training programs and diplomas after boards"
            ]

        return advice

    def run(self, state: LearnerState) -> dict:
        if not state.subjects:
            result = {
                "student_name": state.learner_name,
                "detected_stream": self.detect_stream(state),
                "career_paths": [],
                "top_recommended_path": {},
                "free_cert_count": 0,
                "score_based_advice": [],
                "immediate_actions": [],
                "note": "Insufficient synthetic academic data for career readiness."
            }
            result.update(agent_envelope(
                "Unable to identify career stream based on provided input.",
                ["No degree or specialization matched known patterns", "Fallback to generic guidance"],
                0.3,
                evidence=["Validation Check Failed"]
            ))
            return result

        detected_stream = self.detect_stream(state)
        stream_data = self.career_db.get(detected_stream, self.career_db["science"])

        avg_score = sum(s.percentage for s in state.subjects) / len(state.subjects)
        score_advice = self.get_score_based_advice(state)
        learner_level = state.learner_level
        weakest_name = state.weakest_subject
        strongest_name = state.strongest_subject

        top_path = stream_data["career_paths"][0]
        structured = self.structured_personalization(state, weakest_name)
        career_summary = self.career_summary(state, stream_data["career_paths"], avg_score, weakest_name)
        all_certs = []
        for path in stream_data["career_paths"]:
            for cert in path["certifications"]:
                cert["career_path"] = path["title"]
                all_certs.append(cert)

        free_certs = [c for c in all_certs if "free" in c["cost"].lower()]

        level_actions = {
            "school": ["Build school-level foundations before chasing advanced credentials"],
            "cbse": ["Align career prep with CBSE sample papers and CUET/JEE/NEET as relevant"],
            "university": ["Convert coursework into portfolio projects and internships"],
            "advanced": ["Add research reading, certifications, and public benchmark projects"],
        }

        result = {
            "student_name": state.learner_name,
            "detected_stream": detected_stream,
            "learner_level": learner_level,
            "degree": state.degree,
            "specialization": state.specialization,
            "skill_profile": state.skill_profile,
            "overall_average": round(avg_score, 2),
            "academic_profile": classify_subject(avg_score),
            "weakest_subject": weakest_name,
            "strongest_subject": strongest_name,
            "structured_personalization": structured,
            "career_recommendation": career_summary,
            "career_paths": stream_data["career_paths"],
            "top_recommended_path": next((p for p in stream_data["career_paths"] if p["title"] == career_summary["career"]), top_path),
            "general_skills": stream_data["general_skills"],
            "immediate_actions": level_actions.get(learner_level, level_actions["school"]) + stream_data["immediate_actions"],
            "score_based_advice": score_advice,
            "all_certifications": all_certs,
            "free_certifications": free_certs,
            "free_cert_count": len(free_certs),
            "platforms_to_join": [
                {"name": "Coursera", "url": "https://coursera.org", "why": "Best for certified courses from top universities"},
                {"name": "LinkedIn Learning", "url": "https://linkedin.com/learning", "why": "Industry recognized certificates"},
                {"name": "NPTEL", "url": "https://nptel.ac.in", "why": "Free IIT courses with certificates"},
                {"name": "Swayam", "url": "https://swayam.gov.in", "why": "Free government certified courses"},
                {"name": "Google Skillshop", "url": "https://skillshop.google.com", "why": "Free Google certifications"},
            ],
            "note": "Career data sourced from a synthetic mock database. Connect Foundry IQ for live cited role and certification guidance."
        }
        result.update(agent_envelope(
            f"Recommended {career_summary['career']} readiness path for a {learner_level} learner in {detected_stream}.",
            [
                f"Detected stream as {detected_stream}",
                f"Overall score {avg_score:.1f}% classified as {classify_subject(avg_score).upper()}",
                f"Weakest subject is {weakest_name or 'unknown'}",
                f"Adjusted actions for learner_level={learner_level}",
                *structured.get("reasoning", []),
            ],
            confidence_from_signals(0.84, avg_score / 100),
            self.name,
            ["Accept degree selection without academic checks", "Recommend a static career list only"],
            "Career fit is based on skills, subject performance, learner level, interest, and specialization.",
            evidence=["Stream Suitability Matrix", "Career Opportunity Database"],
        ))

        # Foundry IQ career intelligence
        try:
            from foundry.client import FoundryIQClient
            _fiq = FoundryIQClient()
            student = state.to_student_input()
            avg = sum(s.percentage for s in student.subjects) / len(student.subjects) if student.subjects else 0
            _q = (
                f"Student: {student.name} | Degree: {getattr(student, 'degree', 'N/A')} | "
                f"Stream: {student.stream} | "
                f"Specialization: {getattr(student, 'specialization', 'General')} | "
                f"Average score: {avg:.1f}%.\n"
                f"Suggest top 3 career paths in India with salary ranges in INR, "
                f"3 required skills each, and 2 free certifications to start now."
            )
            ai_career = _fiq.chat(
                context="career_readiness",
                user_message=_q,
                system_prompt="You are a career advisor for Indian tier-2 college students. Be specific about salaries in INR and companies that hire.",
            )
            result["ai_career_advice"] = ai_career
            result["foundry_iq_grounded"] = _fiq.is_live()
            result["foundry_iq_source"] = _fiq.get_source_label()
            result["note"] = f"Career intelligence via {_fiq.get_source_label()}"
        except Exception:
            result["ai_career_advice"] = None
            result["foundry_iq_grounded"] = False

        return result
