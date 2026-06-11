"""Career Readiness Agent Enhanced - Maps scores to skills to LeetCode problems."""
from models.student import StudentInput
from config import config
from typing import Dict, List
from i18n import get_language_manager


class CareerReadinessAgent:
    """Maps student performance to career paths, required skills, and learning resources."""
    
    def __init__(self):
        self.name = "Career Readiness Agent"
        self.lang_manager = get_language_manager()
        self.career_db = self._build_career_database()
        self.skill_resources = self._build_skill_resources()
        self.leetcode_mapping = self._build_leetcode_mapping()
    
    def _build_career_database(self) -> Dict:
        """Build comprehensive career database with skill requirements."""
        return {
            "Computer Science": {
                "roles": [
                    {
                        "title": "Software Engineer",
                        "score_requirement": 65,
                        "salary_min": 6,
                        "salary_max": 25,
                        "demand": "Very High",
                        "core_skills": ["Programming", "DSA", "System Design"],
                        "soft_skills": ["Problem Solving", "Communication"],
                        "required_subjects": ["Computer Science", "Mathematics"],
                        "placement_rate": "92%",
                        "description": "Build and maintain software systems. Focus: Coding, optimization, scalability.",
                        "internship_tips": [
                            "Build 3-5 GitHub projects",
                            "Solve 200+ LeetCode problems",
                            "Contribute to open source",
                            "Practice system design interviews"
                        ]
                    },
                    {
                        "title": "Web Developer",
                        "score_requirement": 60,
                        "salary_min": 5,
                        "salary_max": 20,
                        "demand": "High",
                        "core_skills": ["Frontend", "Backend", "Databases"],
                        "soft_skills": ["UI/UX Thinking", "Creativity"],
                        "required_subjects": ["Computer Science"],
                        "placement_rate": "85%",
                        "description": "Build web applications. Focus: React, Node.js, MongoDB.",
                        "internship_tips": [
                            "Build 3 full-stack projects",
                            "Deploy on AWS/Vercel",
                            "Learn DevOps basics",
                            "Contribute to open source projects"
                        ]
                    },
                    {
                        "title": "Android Developer",
                        "score_requirement": 70,
                        "salary_min": 5,
                        "salary_max": 22,
                        "demand": "High",
                        "core_skills": ["Kotlin", "Android Lifecycle", "Jetpack"],
                        "soft_skills": ["UI Design", "Problem Solving"],
                        "required_subjects": ["Computer Science", "Physics"],
                        "placement_rate": "88%",
                        "description": "Build mobile apps for Android. Focus: Kotlin, Jetpack, Firebase.",
                        "internship_tips": [
                            "Build 3 Android apps",
                            "Learn Firebase integration",
                            "Study Android lifecycle thoroughly",
                            "Publish on Google Play Store"
                        ]
                    },
                    {
                        "title": "Data Scientist",
                        "score_requirement": 75,
                        "salary_min": 8,
                        "salary_max": 30,
                        "demand": "High",
                        "core_skills": ["ML", "Statistics", "Python"],
                        "soft_skills": ["Data Thinking", "Communication"],
                        "required_subjects": ["Mathematics", "Computer Science"],
                        "placement_rate": "87%",
                        "description": "Extract insights from data. Focus: ML, Statistics, Data Visualization.",
                        "internship_tips": [
                            "Participate in Kaggle competitions",
                            "Build 3 ML projects",
                            "Learn Statistics deeply",
                            "Work with synthetic or approved public datasets"
                        ]
                    },
                    {
                        "title": "DevOps Engineer",
                        "score_requirement": 70,
                        "salary_min": 7,
                        "salary_max": 28,
                        "demand": "Very High",
                        "core_skills": ["Docker", "Kubernetes", "CI/CD"],
                        "soft_skills": ["Automation", "Troubleshooting"],
                        "required_subjects": ["Computer Science", "Mathematics"],
                        "placement_rate": "90%",
                        "description": "Maintain deployment infrastructure. Focus: Docker, K8s, AWS.",
                        "internship_tips": [
                            "Learn Docker & Kubernetes",
                            "Set up CI/CD pipelines",
                            "AWS certification",
                            "Hands-on with Linux"
                        ]
                    },
                ]
            },
            "Science": {
                "roles": [
                    {
                        "title": "Data Analyst",
                        "score_requirement": 65,
                        "salary_min": 5,
                        "salary_max": 18,
                        "demand": "High",
                        "core_skills": ["SQL", "Excel", "Python"],
                        "soft_skills": ["Analytical Thinking", "Communication"],
                        "required_subjects": ["Mathematics", "Physics"],
                        "placement_rate": "84%",
                        "description": "Analyze data for insights. Focus: SQL, Python, Tableau.",
                        "internship_tips": [
                            "Master Excel pivottables",
                            "Learn SQL deeply",
                            "Build dashboards",
                            "Practice data storytelling"
                        ]
                    },
                    {
                        "title": "QA Engineer",
                        "score_requirement": 60,
                        "salary_min": 4,
                        "salary_max": 16,
                        "demand": "High",
                        "core_skills": ["Testing", "Automation", "Python"],
                        "soft_skills": ["Attention to Detail", "Communication"],
                        "required_subjects": ["Physics", "Computer Science"],
                        "placement_rate": "82%",
                        "description": "Ensure software quality. Focus: Manual & Automation testing.",
                        "internship_tips": [
                            "Learn Selenium automation",
                            "Understand SDLC",
                            "Write test cases",
                            "Learn Jira/Azure DevOps"
                        ]
                    },
                ]
            }
        }
    
    def _build_skill_resources(self) -> Dict[str, List[Dict]]:
        """Map skills to free learning resources."""
        return {
            "Programming": [
                {"name": "Python for Everybody", "platform": "Coursera", "hours": 30, "cost": "Free to audit"},
                {"name": "Java Programming Masterclass", "platform": "Udemy", "hours": 40, "cost": "Free with financial aid"},
                {"name": "Complete C++ Course", "platform": "Udemy", "hours": 35, "cost": "₹0 discount codes"},
            ],
            "DSA": [
                {"name": "DSA Bootcamp (Python)", "platform": "CodeHelp", "hours": 50, "cost": "₹0 (YouTube)"},
                {"name": "Data Structures & Algorithms", "platform": "Coursera", "hours": 40, "cost": "Free to audit"},
                {"name": "LeetCode DSA Problems", "platform": "LeetCode", "hours": 60, "cost": "Free tier available"},
            ],
            "System Design": [
                {"name": "System Design Course", "platform": "ByteByteGo", "hours": 40, "cost": "₹500-1000"},
                {"name": "Grokking System Design", "platform": "DesignGurus", "hours": 35, "cost": "Free basics"},
            ],
            "Web Development": [
                {"name": "The Complete JavaScript Course", "platform": "Udemy", "hours": 60, "cost": "₹400"},
                {"name": "React Complete Guide", "platform": "Udemy", "hours": 50, "cost": "₹400"},
                {"name": "Node.js Masterclass", "platform": "Udemy", "hours": 45, "cost": "₹400"},
            ],
            "Machine Learning": [
                {"name": "ML Specialization", "platform": "Coursera", "hours": 100, "cost": "Free to audit"},
                {"name": "Fast.ai Practical Deep Learning", "platform": "Fast.ai", "hours": 60, "cost": "Free"},
                {"name": "Kaggle Learn Micro-courses", "platform": "Kaggle", "hours": 30, "cost": "Free"},
            ],
            "Docker & Kubernetes": [
                {"name": "Docker & Kubernetes Course", "platform": "Udemy", "hours": 45, "cost": "₹400"},
                {"name": "Kubernetes for Beginners", "platform": "TechWorld with Nana", "hours": 40, "cost": "Free (YouTube)"},
            ],
            "SQL": [
                {"name": "SQL Masterclass", "platform": "Udemy", "hours": 30, "cost": "₹400"},
                {"name": "SQL Tutorial", "platform": "W3Schools", "hours": 25, "cost": "Free"},
            ],
            "Cloud (AWS)": [
                {"name": "AWS Solutions Architect", "platform": "Udemy", "hours": 50, "cost": "₹400"},
                {"name": "AWS Fundamentals", "platform": "Coursera", "hours": 30, "cost": "Free to audit"},
            ],
        }
    
    def _build_leetcode_mapping(self) -> Dict[str, List[Dict]]:
        """Map skills to LeetCode problem categories and difficulty progression."""
        return {
            "DSA": {
                "easy": ["Two Sum", "Palindrome Number", "Binary Search", "Valid Parentheses"],
                "medium": ["3Sum", "Sort Colors", "Merge Intervals", "Group Anagrams"],
                "hard": ["Median of Two Sorted Arrays", "Word Ladder II", "Binary Tree Max Path Sum"],
                "estimated_problems": 200,
                "timeframe_weeks": 12
            },
            "System Design": {
                "problems": ["Design URL Shortener", "Design LRU Cache", "Design Twitter", "Design Parking Lot"],
                "estimated_problems": 50,
                "timeframe_weeks": 8
            },
            "SQL": {
                "problems": ["Department Highest Salary", "Consecutive Numbers", "Rank Scores"],
                "estimated_problems": 50,
                "timeframe_weeks": 4
            },
        }
    
    def analyze_career_fit(self, student: StudentInput) -> Dict:
        """Analyze which career paths are realistic for the student."""
        lang_manager = get_language_manager()
        
        career_paths = []
        stream_careers = self.career_db.get(student.stream, {}).get("roles", [])
        
        # Calculate overall score
        overall_score = sum(s.percentage for s in student.subjects) / len(student.subjects)
        
        # Get weak subjects
        weak_subjects = [s.name for s in student.get_weak_subjects(threshold=60)]
        strong_subjects = [s.name for s in student.subjects if s.percentage >= 75]
        
        # Analyze each career path
        for career in stream_careers:
            fit_score = self._calculate_career_fit(student, career, overall_score, weak_subjects, strong_subjects)
            
            career_paths.append({
                "title": career["title"],
                "fit_score": fit_score,
                "salary_range": f"₹{career['salary_min']}-{career['salary_max']} LPA",
                "placement_rate": career["placement_rate"],
                "demand": career["demand"],
                "description": career["description"],
                "required_skills": career["core_skills"],
                "learning_path": self._generate_learning_path(career),
                "internship_tips": career["internship_tips"],
                "leetcode_prep": self._get_leetcode_prep(career),
                "roadmap": self._generate_career_roadmap(career)
            })
        
        # Sort by fit score
        career_paths.sort(key=lambda x: x["fit_score"], reverse=True)
        
        return {
            "top_career": career_paths[0] if career_paths else None,
            "all_paths": career_paths,
            "overall_score": round(overall_score, 1),
            "weak_subjects": weak_subjects,
            "strong_subjects": strong_subjects,
            "market_insight": self._get_market_insight(student.stream),
            "actionable_recommendations": self._generate_actionable_recommendations(career_paths, weak_subjects)
        }
    
    def _calculate_career_fit(self, student, career, overall_score, weak_subjects, strong_subjects) -> float:
        """Calculate how well a career matches the student's profile."""
        fit_score = 0
        
        # Base score on overall performance
        if overall_score >= career["score_requirement"]:
            fit_score += 40
        else:
            fit_score += max(0, 40 * (overall_score / career["score_requirement"]))
        
        # Check required subjects alignment
        required_subjects = career["required_subjects"]
        matching_strong = len([s for s in strong_subjects if s in required_subjects])
        fit_score += matching_strong * 15
        
        # Penalty for weak required subjects
        matching_weak = len([s for s in weak_subjects if s in required_subjects])
        fit_score -= matching_weak * 10
        
        # Cap at 100
        return min(100, max(0, fit_score))
    
    def _generate_learning_path(self, career: Dict) -> List[str]:
        """Generate a step-by-step learning path for a career."""
        paths = {
            "Software Engineer": [
                "1. Master Python/Java (2-3 weeks)",
                "2. Learn DSA thoroughly (8-10 weeks, 200+ LeetCode problems)",
                "3. Build 3-5 projects (GitHub portfolio)",
                "4. Learn System Design (4-6 weeks)",
                "5. Prepare for interviews (2-3 weeks)",
                "6. Apply for internships/jobs"
            ],
            "Web Developer": [
                "1. HTML, CSS, JavaScript fundamentals (2 weeks)",
                "2. React frontend framework (3-4 weeks)",
                "3. Node.js & Express backend (3-4 weeks)",
                "4. Database design & SQL (2-3 weeks)",
                "5. Build full-stack projects (4-6 weeks)",
                "6. DevOps basics & deployment (2 weeks)"
            ],
            "Data Scientist": [
                "1. Python & Statistics foundation (4 weeks)",
                "2. Pandas & NumPy for data manipulation (2-3 weeks)",
                "3. Scikit-learn for ML algorithms (4-5 weeks)",
                "4. Data visualization (2 weeks)",
                "5. Deep Learning (TensorFlow/PyTorch) (6-8 weeks)",
                "6. Kaggle competitions & projects (ongoing)"
            ],
            "DevOps Engineer": [
                "1. Linux fundamentals (2-3 weeks)",
                "2. Docker containerization (3-4 weeks)",
                "3. Kubernetes orchestration (4-6 weeks)",
                "4. CI/CD pipelines (Jenkins/GitLab CI) (2-3 weeks)",
                "5. AWS/Cloud platform (4-6 weeks)",
                "6. Infrastructure as Code (Terraform) (2-3 weeks)"
            ],
        }
        return paths.get(career["title"], ["Custom learning path based on career requirements"])
    
    def _get_leetcode_prep(self, career: Dict) -> Dict:
        """Get LeetCode preparation strategy for the career."""
        if career["title"] == "Software Engineer":
            return {
                "target_problems": 200,
                "difficulty": "Easy→Medium→Hard",
                "focus_topics": ["Array", "String", "DP", "Graph", "Tree"],
                "timeframe": "12 weeks",
                "competitive_prep": "Must solve 200+ to be competitive"
            }
        elif career["title"] == "Web Developer":
            return {
                "target_problems": 50,
                "difficulty": "Easy→Medium",
                "focus_topics": ["Array", "String", "Hash Map"],
                "timeframe": "6-8 weeks",
                "note": "Focus on system design & projects over competitive coding"
            }
        else:
            return {
                "target_problems": 30,
                "difficulty": "Easy→Medium",
                "focus_topics": ["SQL", "Array", "String"],
                "timeframe": "4-6 weeks"
            }
    
    def _generate_career_roadmap(self, career: Dict) -> str:
        """Generate a roadmap for the entire career journey."""
        roadmaps = {
            "Software Engineer": "Learn DSA → Build Projects → Internship → Placement → SDE-1 → SDE-2",
            "Web Developer": "Frontend → Backend → Full Stack → Freelance/Job → Senior Developer",
            "Data Scientist": "Python → ML Algorithms → Projects → Internship → Data Science Job",
            "DevOps Engineer": "Linux → Docker → K8s → AWS → Sr. DevOps Engineer",
            "Android Developer": "Java/Kotlin → Android Basics → Projects → Internship → Mobile Developer",
        }
        return roadmaps.get(career["title"], "Career progression path")
    
    def _get_market_insight(self, stream: str) -> Dict:
        """Provide market insights for the stream."""
        insights = {
            "Computer Science": {
                "top_demand_roles": ["DevOps Engineer", "Software Engineer", "Full-Stack Developer"],
                "average_salary": "₹6-25 LPA",
                "growth_trend": "High demand, 15% annual growth",
                "hiring_companies": "Google, Microsoft, Amazon, Flipkart, Ola, Zomato",
                "market_observation": "AI/ML roles growing fastest. Backend/DevOps most stable."
            },
            "Science": {
                "top_demand_roles": ["Data Analyst", "QA Engineer"],
                "average_salary": "₹4-18 LPA",
                "growth_trend": "Moderate demand, 8% annual growth",
                "hiring_companies": "TCS, Infosys, Wipro, Accenture, HCL",
                "market_observation": "Transition to tech requires additional certifications."
            }
        }
        return insights.get(stream, {})
    
    def _generate_actionable_recommendations(self, career_paths: List[Dict], weak_subjects: List[str]) -> List[str]:
        """Generate specific, actionable recommendations."""
        recommendations = []
        
        if career_paths:
            top_career = career_paths[0]
            recommendations.append(f"🎯 Primary Target: {top_career['title']} (Fit: {top_career['fit_score']:.0f}/100)")
            recommendations.append(f"   → Start with: {top_career['learning_path'][0]}")
            
            if weak_subjects:
                recommendations.append(f"⚠️  Improve weak areas first: {', '.join(weak_subjects)}")
                recommendations.append(f"   → This will boost eligibility for: {', '.join([c['title'] for c in career_paths[1:3] if c['fit_score'] > 50])}")
            
            recommendations.append(f"📊 Next step: Complete first module of learning path (2-3 weeks)")
            recommendations.append(f"💼 Target timeline: Get internship within 3-4 months, placement within 6-8 months")
        
        return recommendations
    
    def run(self, student: StudentInput) -> Dict:
        """Main entry point for career analysis."""
        print(f"\n{'='*50}")
        print(f"  {self.name}")
        print(f"{'='*50}\n")
        
        analysis = self.analyze_career_fit(student)
        
        print(f"✓ Analyzed {len(analysis['all_paths'])} career paths")
        if analysis['top_career']:
            print(f"  Top match: {analysis['top_career']['title']} ({analysis['top_career']['fit_score']:.0f}/100)")
        
        return analysis
