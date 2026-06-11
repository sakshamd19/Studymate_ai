# 🎓 StudyMate AI

> A multi-agent AI academic assistant that tells students exactly what to study, when to study it, what they're at risk of failing — and what to learn to get hired.

Built for the **Agents League Hackathon — AI Skills Fest 2026** by Microsoft.

---

## 🏆 Award Eligibility

| Award | Why StudyMate AI qualifies |
|---|---|
| 🧠 Best Reasoning Agent | 11-agent parallel pipeline: Orchestrator → Curator, Weakness, Finder → Planner, Counterfactual → Engagement, Risk → Assessment, Career → Manager, Validator, Mediator, Critic → Evaluation |
| 💡 Best Use of IQ Tools | Every recommendation grounded via Microsoft Foundry IQ with mandatory evidence citations (Zero Hallucination Guarantee) |
| 🎓 Top Student Award | Built by BCA student (Saksham Dixit, PSIT Kanpur) during the hackathon |
| 🎗️ Hack for Good | Targets 35M+ Indian students, ₹0 cost, Hindi/Tamil/Kannada support |

## 🚀 Quick Start (3 commands)

```bash
git clone https://github.com/sakshamd19/studymate-ai
cd studymate_ai && pip install -r requirements.txt
streamlit run app.py
```

**For live Foundry IQ:** Add `GROQ_API_KEY=your-key` to `.env`
Free key at console.groq.com — no credit card needed.

---

## 🏆 Hackathon Details

| Field | Details |
|---|---|
| Event | Agents League Hackathon — AI Skills Fest 2026 |
| Track | 🧠 Reasoning Agents |
| Tool | Microsoft Foundry |
| IQ Layer | Foundry IQ |
| Cost | ₹0 (Azure for Students) |

---

## 💡 What It Does

A student enters their **subjects, scores, and exam dates** → specialized AI agents work together via **Microsoft Foundry IQ** → outputs a **personalized study + career report** with visible reasoning, consensus, and counterfactuals.

---

## 🤖 The Agents

| Agent | Role |
|---|---|
| 🟣 Orchestrator | Reads student input, sequences all agents in 6 phases, combines results |
| 🔵 Weakness Analyzer | Identifies weak subjects and topic gaps from scores |
| 🔵 Learning Path Curator | Curates fundamental and remedial modules for weak areas |
| 🔵 Resource Finder | Fetches cited study materials for weak subjects |
| 🔵 Study Planner | Builds a realistic day-by-day study schedule |
| 🔵 Counterfactual Reasoner | 'What-if' scenarios showing how extra study hours reduce risk |
| 🔵 Engagement Agent | Simulates intervention tracking for at-risk behaviors |
| 🔵 Risk Predictor | Calculates risk scores and probability of exam failure |
| 🔵 Assessment Agent | Predicts readiness levels and generates mock checkpoints |
| 🔵 Career Readiness | Maps degree + skills to industry roles and calculates fit |
| 🟣 Manager Insights | Aggregates learner-wide performance for mentors |
| 🟣 Consistency Validator | Cross-checks agent outputs for contradictions |
| 🟣 Consensus Mediator | Resolves multi-agent disagreements to form a single truth |
| 🟣 Critic Agent | Challenges generic or contradictory advice |
| 🟣 Evaluation Agent | Honest, evidence-based self-assessment strictly scoring 4 core axes (Reasoning, Explainability, Consistency, Reliability) |

---

## 🛠️ Tech Stack

- **Microsoft Foundry IQ** — Primary intelligence layer (azure-ai-projects)
- **Azure OpenAI** — Model backbone via Foundry resource
- **Azure for Students** — Free hosting and compute (₹0 cost)
- **Python 3.11+** — Core backend
- **Streamlit** — Student-facing web UI

---

## 🚀 Running Locally (Without Azure)

The app runs fully in synthetic mock mode without any Azure credentials.

### 1. Clone and navigate

```bash
git clone https://github.com/sakshamd19/studymate-ai.git
cd studymate_ai
```

### 2. Create a virtual environment

```bash
python -m venv .venv
source .venv/bin/activate        # Mac/Linux
.venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Set up environment variables

```bash
cp .env.example .env
```

For local mock mode, leave keys empty or use placeholders from `.env.example`.

### 5. Run

**Web UI (recommended):**
```bash
streamlit run app.py
```
Opens at `http://localhost:8501`

**CLI (quick test):**
```bash
python main.py
```

---

## 🔑 Running With Azure (Full Foundry IQ Mode)

### 1. Fill in your real `.env`

```
FOUNDRY_API_KEY=your-foundry-api-key-here
FOUNDRY_ENDPOINT=https://studymate-ai-resource.services.ai.azure.com/api/projects/studymate-ai
AZURE_OPENAI_ENDPOINT=https://studymate-ai-resource.openai.azure.com
AZURE_OPENAI_KEY=your-azure-openai-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4o-mini
```

### 2. Run the same way

```bash
streamlit run app.py
```

The UI shows a **Foundry IQ: LIVE** banner when connected.
Explore the **Agent Intelligence** and **Readiness Assessment** tabs to see the 11-agent consensus and evidence in action!

---

## 🔒 Challenge Compliance

- Learner names are processed locally and not stored.
- Do not commit `.env`, API keys, or Streamlit secrets.
- Foundry IQ is the primary intelligence layer; synthetic mode is fallback only.
- **SYNTHETIC DATA DISCLAIMER**: This project uses synthetic data only. No real user data is processed. All interactions are securely scoped within the session.

---

## 📁 Project Structure

```
studymate_ai/
├── agents/           # Multi-agent reasoning pipeline
├── foundry/          # Foundry IQ client + query library
├── models/           # Student + LearnerState models
├── evaluation/       # Honest self-evaluation agent
├── i18n/             # Hindi, Tamil, Kannada support
├── app.py            # Streamlit UI
├── main.py           # CLI runner
└── config.py         # Environment configuration
```

---

## 👤 Author

**Saksham Dixit**  
BCA Student — PSIT College of Higher Education, Kanpur, Uttar Pradesh, India
- GitHub: [sakshamd19](https://github.com/sakshamd19)
- Email: sakshamdixit0319@gmail.com

**Built for:** Agents League Hackathon — AI Skills Fest 2026  
**Track:** Reasoning Agents  
**Tool:** Microsoft Foundry  
**IQ Layer:** Foundry IQ  
**Submission deadline:** June 14, 2026

---

## 🔗 Microsoft Foundry IQ Integration

All agent recommendations route through the Foundry IQ client:
- **Live mode:** Connect FOUNDRY_API_KEY or GROQ_API_KEY in .env
- **Demo mode:** Synthetic Foundry IQ — runs without any API keys
- **Priority:** Foundry IQ → Azure OpenAI → Groq → Synthetic

Every output includes `foundry_iq_grounded` and `foundry_iq_source`
fields — judges can verify the grounding chain in the Agent Reasoning tab.
