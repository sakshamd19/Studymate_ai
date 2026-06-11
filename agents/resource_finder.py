from typing import Dict, List
from agents.intelligence import agent_envelope, confidence_from_signals
from foundry.synthetic_iq import SyntheticFoundryIQ
from models.learner_state import LearnerState

class ResourceFinderAgent:
    def __init__(self):
        self.name = "Resource Finder Agent"
        # mock resource database
        # replace with Foundry IQ calls when live grounding is configured
        self.resource_db = {
            "mathematics": {
                "youtube": [
                    {"title": "3Blue1Brown", "url": "https://youtube.com/@3blue1brown", "why": "Best for visual understanding of concepts"},
                    {"title": "Khan Academy Maths", "url": "https://youtube.com/@khanacademy", "why": "Step by step explanations for all topics"},
                    {"title": "Vedantu Maths", "url": "https://youtube.com/@VedantuMath", "why": "Indian curriculum focused, exam oriented"},
                ],
                "websites": [
                    {"title": "Khan Academy", "url": "https://khanacademy.org", "why": "Free structured courses with practice"},
                    {"title": "Brilliant.org", "url": "https://brilliant.org", "why": "Problem solving and deep understanding"},
                    {"title": "Embibe", "url": "https://embibe.com", "why": "Indian exam practice with analysis"},
                ],
                "practice": [
                    {"title": "CBSE past papers", "url": "https://cbse.gov.in", "why": "Official past papers"},
                    {"title": "Toppr Maths", "url": "https://toppr.com", "why": "Chapter wise practice questions"},
                ],
                "key_topics": ["Algebra", "Calculus", "Trigonometry", "Statistics", "Coordinate Geometry"],
                "tip": "Solve at least 10 problems daily. Mathematics only improves with consistent practice."
            },
            "physics": {
                "youtube": [
                    {"title": "Physics Wallah", "url": "https://youtube.com/@PhysicsWallah", "why": "Best free physics for Indian students"},
                    {"title": "Veritasium", "url": "https://youtube.com/@veritasium", "why": "Deep conceptual understanding"},
                    {"title": "The Organic Chemistry Tutor", "url": "https://youtube.com/@TheOrganicChemistryTutor", "why": "Clear explanations of tough topics"},
                ],
                "websites": [
                    {"title": "Physics Classroom", "url": "https://physicsclassroom.com", "why": "Concept tutorials and simulations"},
                    {"title": "HyperPhysics", "url": "http://hyperphysics.phy-astr.gsu.edu", "why": "Quick concept reference"},
                    {"title": "BYJU'S Physics", "url": "https://byjus.com/physics", "why": "Indian curriculum with examples"},
                ],
                "practice": [
                    {"title": "DC Pandey Solutions", "url": "https://vedantu.com/books/dc-pandey", "why": "Best problem book for physics"},
                    {"title": "Previous year JEE papers", "url": "https://jeemain.nta.nic.in", "why": "High quality physics problems"},
                ],
                "key_topics": ["Mechanics", "Thermodynamics", "Electromagnetism", "Optics", "Modern Physics"],
                "tip": "Draw diagrams for every problem. Physics is visual — understanding the setup is half the solution."
            },
            "chemistry": {
                "youtube": [
                    {"title": "Chemistry Wallah", "url": "https://youtube.com/@ChemistryWallah", "why": "Excellent for Indian board and JEE chemistry"},
                    {"title": "Crash Course Chemistry", "url": "https://youtube.com/@crashcourse", "why": "Fast and clear concept videos"},
                    {"title": "Tyler DeWitt", "url": "https://youtube.com/@tylerdewitt", "why": "Makes complex chemistry simple"},
                ],
                "websites": [
                    {"title": "ChemLibreTexts", "url": "https://chem.libretexts.org", "why": "Free comprehensive chemistry textbook"},
                    {"title": "Royal Society of Chemistry", "url": "https://www.rsc.org/learn-chemistry", "why": "High quality learning resources"},
                    {"title": "BYJU'S Chemistry", "url": "https://byjus.com/chemistry", "why": "Indian curriculum focused"},
                ],
                "practice": [
                    {"title": "NCERT Chemistry", "url": "https://ncert.nic.in", "why": "Foundation for all Indian exams"},
                    {"title": "Narendra Awasthi Problems", "url": "https://amazon.in", "why": "Best physical chemistry problems"},
                ],
                "key_topics": ["Organic Chemistry", "Physical Chemistry", "Chemical Bonding", "Electrochemistry", "Equilibrium"],
                "tip": "Memorize periodic table trends and reaction mechanisms. Organic chemistry needs daily revision."
            },
            "biology": {
                "youtube": [
                    {"title": "Amoeba Sisters", "url": "https://youtube.com/@AmoebaSisters", "why": "Fun and clear biology explanations"},
                    {"title": "Ninja Nerd", "url": "https://youtube.com/@NinjaNerdScience", "why": "Detailed medical biology content"},
                    {"title": "Biology Wallah", "url": "https://youtube.com/@PhysicsWallah", "why": "Indian board biology focused"},
                ],
                "websites": [
                    {"title": "Khan Academy Biology", "url": "https://khanacademy.org/science/biology", "why": "Structured free biology courses"},
                    {"title": "NCERT Biology", "url": "https://ncert.nic.in", "why": "Must read for Indian board exams"},
                    {"title": "Visible Body", "url": "https://visiblebody.com", "why": "3D anatomy and physiology"},
                ],
                "practice": [
                    {"title": "NEET previous papers", "url": "https://neet.nta.nic.in", "why": "Best biology MCQ practice"},
                    {"title": "Trueman's Biology", "url": "https://amazon.in", "why": "Comprehensive for board exams"},
                ],
                "key_topics": ["Cell Biology", "Genetics", "Human Physiology", "Plant Biology", "Ecology"],
                "tip": "Biology is mostly memory-based. Use diagrams, flowcharts and mnemonics to retain information longer."
            },
            "english": {
                "youtube": [
                    {"title": "English with Lucy", "url": "https://youtube.com/@EnglishwithLucy", "why": "Excellent grammar and vocabulary"},
                    {"title": "BBC Learning English", "url": "https://youtube.com/@bbclearningenglish", "why": "Professional and structured lessons"},
                    {"title": "TED Talks", "url": "https://youtube.com/@TED", "why": "Improve comprehension and vocabulary"},
                ],
                "websites": [
                    {"title": "Grammarly Blog", "url": "https://grammarly.com/blog", "why": "Grammar rules and writing tips"},
                    {"title": "BBC Learning English", "url": "https://bbc.co.uk/learningenglish", "why": "Free structured English lessons"},
                    {"title": "Purdue OWL", "url": "https://owl.purdue.edu", "why": "Best resource for writing skills"},
                ],
                "practice": [
                    {"title": "CBSE English papers", "url": "https://cbse.gov.in", "why": "Official exam pattern practice"},
                    {"title": "Wordsmith", "url": "https://wordsmith.org", "why": "Daily vocabulary building"},
                ],
                "key_topics": ["Grammar", "Reading Comprehension", "Writing Skills", "Literature", "Vocabulary"],
                "tip": "Read an English article or chapter every day. Writing skills improve only through regular practice."
            },
            "computer science": {
                "youtube": [
                    {"title": "CS50 Harvard", "url": "https://youtube.com/@cs50", "why": "Best computer science foundation course"},
                    {"title": "Apna College", "url": "https://youtube.com/@ApnaCollegeOfficial", "why": "Perfect for Indian CS students"},
                    {"title": "Kunal Kushwaha", "url": "https://youtube.com/@KunalKushwaha", "why": "DSA and programming for beginners"},
                ],
                "websites": [
                    {"title": "GeeksforGeeks", "url": "https://geeksforgeeks.org", "why": "Complete CS reference for Indian exams"},
                    {"title": "W3Schools", "url": "https://w3schools.com", "why": "Quick reference for programming"},
                    {"title": "LeetCode", "url": "https://leetcode.com", "why": "Best for programming practice"},
                ],
                "practice": [
                    {"title": "CBSE CS past papers", "url": "https://cbse.gov.in", "why": "Official exam pattern"},
                    {"title": "CodeChef", "url": "https://codechef.com", "why": "Competitive programming practice"},
                ],
                "key_topics": ["Programming Basics", "Data Structures", "Algorithms", "DBMS", "Networking"],
                "tip": "Code every single day even for 30 minutes. Reading code and writing code are very different skills."
            },
            "economics": {
                "youtube": [
                    {"title": "Crash Course Economics", "url": "https://youtube.com/@crashcourse", "why": "Quick and clear economics concepts"},
                    {"title": "Khan Academy Economics", "url": "https://khanacademy.org/economics-finance-domain", "why": "Structured macro and micro economics"},
                    {"title": "NCERT Wallah Economics", "url": "https://youtube.com/@PhysicsWallah", "why": "Indian board economics focused"},
                ],
                "websites": [
                    {"title": "Khan Academy Economics", "url": "https://khanacademy.org/economics-finance-domain", "why": "Free structured economics courses"},
                    {"title": "Investopedia", "url": "https://investopedia.com", "why": "Real world economics concepts"},
                    {"title": "NCERT Economics", "url": "https://ncert.nic.in", "why": "Foundation for Indian board exams"},
                ],
                "practice": [
                    {"title": "CBSE Economics papers", "url": "https://cbse.gov.in", "why": "Official past year papers"},
                    {"title": "Sandeep Garg Solutions", "url": "https://amazon.in", "why": "Best economics guide for boards"},
                ],
                "key_topics": ["Microeconomics", "Macroeconomics", "National Income", "Money and Banking", "Statistics"],
                "tip": "Draw supply-demand diagrams for every concept. Economics becomes much clearer with visual representation."
            },
            "history": {
                "youtube": [
                    {"title": "Crash Course History", "url": "https://youtube.com/@crashcourse", "why": "Engaging and detailed history videos"},
                    {"title": "Historia Civilis", "url": "https://youtube.com/@HistoriaCivilis", "why": "Deep historical analysis"},
                    {"title": "NCERT History Wallah", "url": "https://youtube.com/@PhysicsWallah", "why": "Indian board history focused"},
                ],
                "websites": [
                    {"title": "NCERT History", "url": "https://ncert.nic.in", "why": "Primary source for Indian board exams"},
                    {"title": "History.com", "url": "https://history.com", "why": "Detailed articles on world history"},
                    {"title": "Ancient History Encyclopedia", "url": "https://worldhistory.org", "why": "Reliable historical reference"},
                ],
                "practice": [
                    {"title": "CBSE History papers", "url": "https://cbse.gov.in", "why": "Official past year questions"},
                    {"title": "Arihant History Guide", "url": "https://amazon.in", "why": "Comprehensive board exam guide"},
                ],
                "key_topics": ["Ancient History", "Medieval History", "Modern History", "World Wars", "Indian Independence"],
                "tip": "Create timelines and connect events to causes and effects. History is a story — understand it, don't just memorize it."
            }
        }
        self.synthetic_iq = SyntheticFoundryIQ()

    def learner_level_resources(self, learner_level: str) -> Dict[str, List[dict]]:
        level = (learner_level or "school").lower()
        if level in {"school", "cbse"}:
            return {
                "curated": [
                    {"title": "NCERT Official", "url": "https://ncert.nic.in", "why": "School syllabus-aligned concept and exercise base"},
                    {"title": "CBSE Academic", "url": "https://cbseacademic.nic.in", "why": "Synthetic CBSE-aligned syllabus and sample-paper grounding"},
                    {"title": "Khan Academy", "url": "https://khanacademy.org", "why": "Concept explanations and practice for school learners"},
                ],
            }
        if level == "university":
            return {
                "curated": [
                    {"title": "MIT OpenCourseWare", "url": "https://ocw.mit.edu", "why": "Deep lecture notes and problem sets"},
                    {"title": "Coursera", "url": "https://coursera.org", "why": "University-level guided courses"},
                    {"title": "NPTEL", "url": "https://nptel.ac.in", "why": "IIT/IISc course lectures and assignments"},
                ],
            }
        if level == "advanced":
            return {
                "curated": [
                    {"title": "Official Documentation", "url": "https://learn.microsoft.com", "why": "Applied technical references and API behavior"},
                    {"title": "GitHub Projects", "url": "https://github.com", "why": "Portfolio-grade implementation examples"},
                    {"title": "Research Benchmarks", "url": "https://paperswithcode.com", "why": "Paper-linked tasks and reproducible benchmarks"},
                ],
            }
        return {
            "curated": [
                {"title": "NCERT Official", "url": "https://ncert.nic.in", "why": "Syllabus-aligned synthetic school baseline"},
                {"title": "Khan Academy", "url": "https://khanacademy.org", "why": "School-friendly explanations and practice"},
            ],
        }

    def get_default_resources(self, subject_name: str) -> dict:
        return {
            "youtube": [
                {"title": "Khan Academy", "url": "https://youtube.com/@khanacademy", "why": "Covers most academic subjects clearly"},
                {"title": "Physics Wallah", "url": "https://youtube.com/@PhysicsWallah", "why": "Best free resource for Indian students"},
            ],
            "websites": [
                {"title": "Khan Academy", "url": "https://khanacademy.org", "why": "Free structured learning"},
                {"title": "NCERT Official", "url": "https://ncert.nic.in", "why": "Foundation for all Indian exams"},
            ],
            "practice": [
                {"title": "CBSE official papers", "url": "https://cbse.gov.in", "why": "Official exam past papers"},
            ],
            "key_topics": [f"Review your {subject_name} syllabus and focus on high-weightage chapters"],
            "tip": f"Consistency is key for {subject_name}. Study a little every day rather than cramming."
        }

    def find_resources_for_subject(
        self,
        subject_name: str,
        weakness_level: str,
        learner_level: str = "school",
        *,
        degree: str = "",
        specialization: str = "",
        is_weakest: bool = False,
    ) -> dict:
        key = subject_name.lower().strip()

        # try to match subject name
        resources = None
        for db_key in self.resource_db:
            if db_key in key or key in db_key:
                resources = self.resource_db[db_key]
                break

        if not resources:
            resources = self.get_default_resources(subject_name)

        level_resources = self.learner_level_resources(learner_level)
        iq = self.synthetic_iq.query(subject_name, learner_level, weakness_level, degree, specialization)
        selection_reason = (
            f"Selected for {learner_level} learner"
            + (f", degree {degree}" if degree else "")
            + (f", specialization {specialization}" if specialization else "")
            + (" — weakest-subject priority" if is_weakest else "")
        )

        if weakness_level == "strong":
            result = {
                "subject": subject_name,
                "weakness_level": weakness_level,
                "classification": weakness_level,
                "learner_level": learner_level,
                "message": f"{subject_name} is on track. Light revision resources only.",
                "curated_resources": level_resources["curated"][:2],
                "key_topics": resources["key_topics"],
                "tip": resources["tip"],
                "grounding": iq,
                "selection_reason": selection_reason,
            }
        else:
            result = {
                "subject": subject_name,
                "weakness_level": weakness_level,
                "classification": weakness_level,
                "learner_level": learner_level,
                "curated_resources": level_resources["curated"][:3],
                "key_topics": resources["key_topics"],
                "tip": resources["tip"],
                "grounding": iq,
                "source": "synthetic_mock_db",
                "selection_reason": selection_reason,
            }

        resources = result
        # Foundry IQ live resource enhancement
        try:
            from foundry.client import FoundryIQClient
            _fiq = FoundryIQClient()
            _q = (
                f"Subject: {subject_name} | Weakness level: {weakness_level}.\n"
                f"Recommend top free study resources for an Indian university student: "
                f"2 YouTube channels with specific playlists, 2 websites, 1 practice paper source."
            )
            ai_resources = _fiq.chat(
                context="resource_finding",
                user_message=_q,
                system_prompt="You are a curated resource specialist for Indian students. Only free resources.",
            )
            resources["ai_curated_resources"] = ai_resources
            resources["foundry_iq_grounded"] = _fiq.is_live()
            resources["foundry_iq_source"] = _fiq.get_source_label()
            resources["source"] = _fiq.get_source_label() if _fiq.is_live() else "mock_db"
        except Exception:
            resources["foundry_iq_grounded"] = False
            resources["source"] = "mock_db"

        return result

    def run(self, state: LearnerState, weakness_analysis: dict | None = None) -> dict:
        all_analyses = (weakness_analysis or {}).get("all_analyses", [])
        if not all_analyses:
            all_analyses = state.priority_ranking
        subject_resources = []
        learner_level = state.learner_level

        ranked = state.ranked_subjects or [a.get("subject") for a in all_analyses]
        sorted_analyses = sorted(
            all_analyses,
            key=lambda a: ranked.index(a["subject"]) if a["subject"] in ranked else 99,
        )

        import concurrent.futures
        def _process_resource(analysis):
            return self.find_resources_for_subject(
                analysis["subject"],
                analysis.get("weakness_level", analysis.get("classification", "moderate")),
                learner_level,
                degree=state.degree,
                specialization=state.specialization,
                is_weakest=analysis["subject"] == state.weakest_subject,
            )

        with concurrent.futures.ThreadPoolExecutor(max_workers=min(10, max(1, len(sorted_analyses)))) as executor:
            subject_resources = list(executor.map(_process_resource, sorted_analyses))

        weak_resources = [r for r in subject_resources if r["weakness_level"] == "weak"]
        good_resources = [r for r in subject_resources if r["weakness_level"] == "strong"]
        iq_summary = {
            "answer": "Synthetic Foundry IQ grounding used for resource selection.",
            "sources": sorted({source for r in subject_resources for source in r.get("grounding", {}).get("sources", [])}) or ["Synthetic Guide", "Mock Dataset"],
        }

        result = {
            "total_subjects": len(subject_resources),
            "weak_subjects_covered": len(weak_resources),
            "learner_level": learner_level,
            "subject_resources": subject_resources,
            "weak_resources": weak_resources,
            "good_resources": good_resources,
            "synthetic_iq": iq_summary,
            "general_tools": [
                {"name": "Notion", "url": "https://notion.so", "use": "Organize notes and study plans"},
                {"name": "Anki", "url": "https://apps.ankiweb.net", "use": "Flashcards for memorization"},
                {"name": "Forest App", "url": "https://forestapp.cc", "use": "Stay focused while studying"},
                {"name": "Pomodoro Timer", "url": "https://pomofocus.io", "use": "25 min study + 5 min break cycles"},
            ],
            "note": "Resources sourced from a synthetic mock database. Connect Foundry IQ for live cited retrieval from approved knowledge sources."
        }
        result.update(agent_envelope(
            f"Selected {learner_level}-appropriate resources with synthetic IQ citations.",
            [
                f"Detected learner_level as {learner_level}",
                "Mapped level to non-generic resource families",
                "Queried synthetic knowledge base for grounded answer and sources",
                "Reduced resources for STRONG subjects and expanded practice for WEAK subjects",
            ],
            confidence_from_signals(0.86, len(subject_resources) / 8 if subject_resources else 0.3),
            self.name,
            ["Mixed CBSE/university/advanced resource stack", "Unbounded generic link list"],
            "Resources are limited to two or three curated links from the learner's level only.",
            evidence=iq_summary.get("sources", ["Curated URL Database"]),
        ))
        return result
