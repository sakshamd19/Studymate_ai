# StudyMate AI — Rejection Audit (Phase 0)

**Audit date:** 2026-06-06  
**Scope:** Full repository review before coherence refactor  
**Auditor role:** Principal Architect / Final-Round Judge (hostile review lens)

This document catalogs every material rejection risk found in the current codebase. No logic changes were made during this audit.

---

## Executive Summary

StudyMate AI has substantial backend reasoning infrastructure (weakness ranking, risk formula, critic, counterfactuals, evaluation, consensus mediator) but **judges cannot see most of it in the UI**. Worse, **agents do not share a single canonical learner state**, so weakest-subject identity, confidence, and degree context can diverge across outputs. Several features are **hardcoded to Physics** or **stream-only**, and validation **blocks normal synthetic IDs** unless they use `L-` or `SYN-` prefixes.

**Highest rejection vectors:**
1. Hidden intelligence (consensus, full counterfactuals, evaluation, observability not in UI)
2. Inconsistent weakest-subject derivation across agents
3. Hostile learner-ID validation in `app.py` path (UI allows any text; orchestrator rejects)
4. Career logic dominated by stream detection, not degree/specialization/skill maturity
5. Self-evaluation scoring routinely reports 98–100/100 without behavioral proof
6. Consensus mediator hardcoded to Physics
7. Stale session state when learner level / subject count changes
8. `main.py` CLI crashes on resource output shape change

---

## 1. Crash Risks

| Risk | Location | Detail |
|------|----------|--------|
| **KeyError on resource print** | `main.py:74-79` | `print_report()` expects `weak_resources[].youtube` and `.websites`, but `ResourceFinderAgent` now returns `curated_resources` only. Verified crash: `KeyError: 'youtube'`. |
| **Division by zero in study plan** | `agents/study_planner.py:219` | `total_hours / len(schedule)` if schedule is empty (e.g., all past exam dates). |
| **Past exam dates silently drop risk** | `agents/risk_predictor.py:116-118` | Subjects with `days_until_exam < 0` are excluded from risk analysis entirely → `total_subjects_analyzed: 0`, but weakness/plan may still run. |
| **Past exam dates in UI blocked** | `app.py:126` | `min_value=date.today()` prevents selecting past dates in UI, but CLI/API paths can still pass them → inconsistent behavior. |
| **Empty subjects after validation** | `agents/orchestrator.py:22-41` | On validation failure, all agent slots get the same `agent_envelope` failsafe dict; UI tabs expect nested keys like `all_analyses`, `daily_schedule` → potential KeyError if UI doesn't guard. |
| **Synthetic IQ KB missing** | `foundry/synthetic_iq.py:9` | Falls back to empty entries; does not crash but returns generic grounding. |
| **Real Foundry IQ** | `foundry/client.py:21-25` | Raises `NotImplementedError` if non-mock API key set — demo crash if judge configures real key. |
| **Unbounded orchestrator exception** | `app.py:169-170` | Generic `except Exception` shows message but any unexpected agent failure surfaces as user error. |

---

## 2. Stale-State Risks

| Risk | Location | Detail |
|------|----------|--------|
| **Report persists after form edits** | `app.py:29-34, 172+` | `st.session_state.report` shown whenever `analyzed=True`. Changing learner level, subject count, degree, or specialization does **not** clear report until re-submit. Judge can edit inputs and still see old analysis. |
| **No level-confirmation gate** | `app.py:63-134` | All fields visible in one form; no stepwise confirm-level → reveal-degree → analyze flow. |
| **Subject widget keys survive count change** | `app.py:110-128` | `key=f"sub_{i}"` — Streamlit may retain values for indices when `num_subjects` decreases, leaving phantom subject data in session until full reset. |
| **Stream overwritten conditionally** | `app.py:68-81` | University path keeps first `stream` selectbox value even when degree hierarchy is the meaningful context; school path overwrites with second selectbox. Stale stream can linger in `st.session_state.student`. |
| **Reset only via form button** | `app.py:136-140` | No automatic invalidation on learner_level / num_subjects / degree change. |
| **Degree fields not cleared on level switch** | `app.py:76-100` | When switching school ↔ university within same session (without reset), `degree_group/degree/specialization` variables are re-bound but old report still displayed. |

---

## 3. Duplicated UI Paths

| Duplication | Location | Detail |
|-------------|----------|--------|
| **Double stream selectbox** | `app.py:68-74` + `app.py:81` | All users see "Your stream" (CS, PCM, Commerce…). School/CBSE users see a **second** "School stream" that overwrites `stream`. University users still see the irrelevant first stream picker. |
| **Degree catalog duplicated** | `app.py:83-97` vs `agents/career_readiness.py:9-34` | Same hierarchy defined in UI and agent; can drift. |
| **Two career agent implementations** | `agents/career_readiness.py` (used) vs `agents/career_readiness_v2.py` (unused) | Dead parallel implementation — judge may find v2 features claimed but not wired. |
| **CLI vs UI report paths** | `main.py` vs `app.py` | Different output shapes; CLI crashes on resources, UI works. |
| **Weakness ranking in two places** | `agents/weakness_analyzer.py:108` (priority_score) vs `agents/career_readiness.py:487` (percentage only) | Same concept, different sort keys. |

---

## 4. Unused or Underused Inputs

| Input | Collected | Actually used | Location |
|-------|-----------|---------------|----------|
| **Interest** | `app.py:76` | Only in `career_readiness.structured_personalization` for AI→TECH nudge | `agents/career_readiness.py:372-374` |
| **Degree group / degree / specialization** | `app.py:98-100` | Warnings only (AI+weak math); not passed to study planner, risk, resources | `agents/career_readiness.py:359-398` |
| **Learner level** | `app.py:75` | Resources + career level_actions; **not** study planner or risk | `agents/resource_finder.py:254`, `agents/career_readiness.py:502-507` |
| **Stream (university users)** | `app.py:68-74` | Career `detect_stream()`; conflicts with degree selection | `agents/career_readiness.py:336-357` |
| **Subject confidence** | Not collected | Computed internally from fixed signals (0.9, data_quality, exam_signal) — not user-supplied | `agents/intelligence.py:56-59` |
| **Skill profile** | Not present | Referenced in hackathon requirements but no model field | `models/student.py` |
| **i18n / LanguageManager** | `i18n/translator.py` | Imported by consensus/career_v2 but **UI is English-only** | `app.py` has no language selector |
| **Foundry IQ live path** | `foundry/client.py` | Never called by resource agent; uses `SyntheticFoundryIQ` instead | `agents/resource_finder.py:223` |

---

## 5. Hidden Features (Backend-Only Intelligence)

These run in the orchestrator but are **not shown in `app.py`**:

| Feature | Produced | UI exposure |
|---------|----------|-------------|
| **Consensus Mediator** | `report.consensus` when `include_advanced_reasoning=True` | Never called from UI; default `False` → **consensus always empty** |
| **Full counterfactual scenarios** | `CounterfactualReasoner.run()` | UI shows nothing; orchestrator only runs lightweight `what_if_study_hours_increase` by default (`orchestrator.py:116-128`) |
| **Critic Agent** | `report.critic_review` | Not displayed in any tab |
| **Evaluation Agent** | `report.evaluation` (scores up to 100) | Not displayed |
| **Observability / latency chain** | `report.observability` | Not displayed |
| **Safety status** | `report.safety_status` | Not displayed (user only sees generic error on failure) |
| **Agent reasoning traces** | `reasoning_trace`, `why_this_decision`, `rejected_options` on each agent | Not displayed in weakness/risk/plan/resource/career tabs |
| **Study plan priority strategy** | `study_plan.priority_strategy` | Not displayed |
| **Synthetic IQ grounding per subject** | `resources.subject_resources[].grounding` | Not displayed |
| **Mock Exam Agent** | `report.mock_exam` when `include_mock_exam=True` | Never enabled from UI |
| **career_readiness_v2** | Full skill/LeetCode mapping | File exists, never imported |

**Judge impact:** Demo looks like a 5-tab template viewer, not a reasoning system.

---

## 6. Independent State Recomputation (No Single Source of Truth)

There is **no `LearnerState`** object. `StudentInput` holds raw inputs only; each agent derives its own view.

| Computation | Who recomputes | Method | Can diverge? |
|-------------|----------------|--------|--------------|
| **Weakest subject** | Weakness Analyzer | `priority_score` sort | Canonical for weakness only |
| **Weakest subject** | Career Agent | `sorted(subjects, key=percentage)` | **Yes** — ignores confidence & exam urgency |
| **Weakest subject** | Counterfactual | `get_weak_subjects(threshold=60)` — first in list order, not priority | **Yes** |
| **Subject classification** | Weakness, Risk, Resources | Shared `classify_subject()` in `intelligence.py` | Mostly aligned |
| **Priority score** | Weakness, Risk | Shared `priority_score()` | Aligned when both call it |
| **Priority score** | Study Planner | Reads from weakness_analysis output | Aligned if weakness ran first |
| **Confidence** | Risk, Weakness | `subject_confidence()` — synthetic, not user input | Same formula, but not true "learner confidence" |
| **Stream / career fit** | Career only | `detect_stream()` heuristics | Ignores degree/specialization for path list |
| **Risk ranking** | Risk Agent | Own `calculate_risk_score()` | Uses shared formula but **does not read** weakness_analysis weakest_subject |

**Missing canonical fields:** `ranked_subjects`, `moderate_subjects`, `strongest_subject`, `days_remaining`, `study_capacity`, `risk_profile`, `confidence_profile`, `skill_profile`, `prior_state`.

---

## 7. Agent Contradiction Points

| Contradiction | Agents involved | Evidence |
|---------------|-----------------|----------|
| **Different weakest subject** | Weakness vs Career vs Counterfactual | Priority sort vs percentage sort vs threshold list order |
| **Risk "most at risk" vs weakness "weakest"** | Risk vs Weakness | Risk sorts by `risk_score`; weakness by `priority_score`. Usually correlated but not guaranteed identical when confidence/exam differ |
| **Career recommends AI/Data while math weak** | Career vs Weakness | Partially handled via warnings (`career_readiness.py:368-370`) but career list still stream-static |
| **Study plan tip vs risk verdict** | Study Planner vs Risk | Planner may say "maintain" while risk says "HIGH" for same subject — no cross-check |
| **Resource level vs subject DB** | Resource Finder | `learner_level_resources()` returns university links, but `resource_db` practice links are CBSE/JEE for all levels (`resource_finder.py:23-25, 159-190`) |
| **Consensus assumes Physics** | Consensus vs actual learner | `consensus_mediator.py:41-63` searches for `"physics"` in subject names — fails silently for non-Physics learners |
| **Critic always finds flaws** | Critic vs Evaluation | Critic lists flaws even when plan is good; Evaluation still scores 98-100 (`evaluation/evaluator.py:44-54`) |
| **Counterfactual risk vs Risk Agent** | Counterfactual vs Risk | Counterfactual uses projected_avg thresholds; Risk uses priority formula — not linked |

---

## 8. Templated vs Adaptive Logic

| Area | Current behavior | Adaptive? |
|------|------------------|-----------|
| **Weakness suggestions** | Fixed 4-5 bullets per weak/moderate/strong tier | Subject name inserted, but same structure every time (`weakness_analyzer.py:27-46`) |
| **Study focus areas** | Rotating cycles for weak; generic templates (`study_planner.py:22-40, 145-165`) | Some day-variation, but not degree/specialization aware |
| **Recovery plans** | Fixed 3-4 steps per risk tier (`risk_predictor.py:48-68`) | Not tied to learner level or degree |
| **Career paths** | Static lists per stream key (`career_readiness.py:38-334`) | Same 3 paths per stream for every user |
| **Score-based advice** | 4 tiers by average only (`career_readiness.py:427-460`) | Ignores specialization, confidence, skill profile |
| **Counterfactual scenarios** | Fixed +18% improvement, +10/5/2% balanced (`counterfactual_reasoner.py:77-115`) | Not re-running agents on modified state |
| **Counterfactual topics** | Hardcoded Physics/Math topic lists (`counterfactual_reasoner.py:255-260`) | Not dynamic by actual weakest subject |
| **Evaluation scores** | Checklist gates → 16-25 per category (`evaluation/evaluator.py:44-54`) | Not observing cross-agent consistency |
| **Consensus** | Average confidence = agreement (`consensus_mediator.py:183-190`) | Not true disagreement detection |

---

## 9. UI Collects Data But Downstream Ignores It

| UI field | Downstream usage gap |
|----------|---------------------|
| **Degree / specialization** | Stored on `StudentInput` but study planner, risk, resources never read them |
| **Interest** | Minimal career nudge only |
| **Learner level (university)** | Study hours caps same for all levels (`config.py:42-44`) |
| **Stream for university** | Misleading; career uses `detect_stream()` which may disagree with degree group TECH vs BUSINESS |
| **Confirm Inputs button** | Triggers full pipeline immediately — no separate "Analyze" step after confirming profile |

---

## 10. Known Problem Classes (Explicit Checklist)

### 10.1 Input validation blocks real users unnecessarily
- **CRITICAL:** `agents/intelligence.py:110-111` rejects learner IDs not starting with `L-` or `SYN-`. UI placeholder says `L-1001` but does not enforce; any judge typing `DEMO-1` or `Student-A` gets full pipeline block with failsafe message.
- PII check flags `@` in text (`intelligence.py:103-105`) — reasonable for compliance.
- Adversarial term blocking is reasonable (`intelligence.py:92-101`).

### 10.2 Duplicate selectboxes / widget collisions
- **Confirmed:** Dual stream selectboxes (`app.py:68-81`).
- University users see stream + degree_group + degree + specialization — cluttered, stream redundant.

### 10.3 Unimplemented grounding or retrieval paths
- `FoundryIQClient._real_query()` → `NotImplementedError` (`foundry/client.py:21-25`).
- `ResourceFinderAgent` uses `SyntheticFoundryIQ` + static `resource_db`, not `FoundryIQClient` (`resource_finder.py:223`).
- README acknowledges gap (`README.md:138`).

### 10.4 Hardcoded subject logic
- **Physics hardcoded in consensus:** `consensus_mediator.py:41-63, 66`.
- **Physics/Math topics in counterfactual:** `counterfactual_reasoner.py:255-260`.
- **Mathematics check for AI careers:** `career_readiness.py:368-370, 411-412`.
- **Subject-specific resource DB keys:** fixed set of ~8 subjects (`resource_finder.py:11-156`).

### 10.5 Self-evaluation inflates scores
- `evaluation/evaluator.py:44-54` — binary rubric checks yield **98-100** for normal/weak/high cases (see `test_results.md`).
- `creativity_score` granted if counterfactuals dict exists — even lightweight hours-only counterfactual counts.
- `reasoning_score: 25` if traces exist — traces can be generic template text.
- No consistency_score, personalization_score, or robustness_score as required by Phase 16.
- `main.py:107-109` prints `/10` but evaluator uses `/100` scale — misleading CLI output.

### 10.6 Hidden reasoning features never shown in UI
- **Confirmed:** No "Agent Reasoning" tab. Critic, consensus, counterfactuals (full), evaluation, observability all hidden.

### 10.7 Career logic tied too heavily to stream selection
- `detect_stream()` drives entire `career_db` lookup (`career_readiness.py:336-357, 481-482`).
- Degree/specialization only affect warnings and hierarchy metadata, not career path selection.
- `career_summary()` adjusts match by interest keyword only (`career_readiness.py:408-410`).
- University learner with BBA still gets stream-detected paths if subjects look like science.

### 10.8 Resource selection mixes school / university / professional levels
- `learner_level_resources()` provides level-appropriate curated links (`resource_finder.py:159-190`).
- BUT `resource_db` defaults include CBSE past papers, NCERT, JEE for all (`resource_finder.py:23-25, 192-207`).
- `get_default_resources()` always returns CBSE/NCERT (`resource_finder.py:198-204`).
- Weak-subject resources no longer expose per-subject youtube/websites in output — only `curated_resources` (level-aware) + generic `key_topics` from school-oriented DB.

---

## 11. Additional Structural Risks

| Issue | Location |
|-------|----------|
| **No ConsistencyValidator** | Not implemented anywhere |
| **No PriorityEngine module** | `priority_score()` in `intelligence.py` — not a shared engine consumed under one contract |
| **No input normalization** | "B.Tech", "btech", "Math" vs "Mathematics" not normalized |
| **Duplicate subjects** | `get_subject_by_name()` returns first match only (`models/student.py:37-38`); no dedup |
| **One subject only** | Works but moderate/strong lists empty — copy may say "several subjects" incorrectly |
| **Equal marks across subjects** | `priority_score` tie-breaker uses percentage then days then name (`weakness_analyzer.py:108`) — arbitrary |
| **Confidence does not affect study hours** | `get_daily_hours()` uses weakness_level only (`study_planner.py:14-20`) |
| **High score + low confidence** | Cannot occur — confidence is synthetic, not user-supplied |
| **Agent count mismatch** | README/UI say 6 agents; orchestrator runs 6 + counterfactual + critic + evaluation = 9 |
| **Tests don't cover UI stale state** | `tests/strict_qa_tests.py` — backend only |
| **pycache committed** | Git status shows `__pycache__` modifications — hygiene risk for judges |

---

## 12. File Reference Index

| Component | Primary files |
|-----------|---------------|
| UI | `app.py` |
| Models | `models/student.py` |
| Orchestration | `agents/orchestrator.py` |
| Shared helpers | `agents/intelligence.py`, `config.py` |
| Agents | `agents/weakness_analyzer.py`, `study_planner.py`, `risk_predictor.py`, `resource_finder.py`, `career_readiness.py`, `critic_agent.py`, `counterfactual_reasoner.py`, `consensus_mediator.py` |
| Unused / partial | `agents/career_readiness_v2.py`, `agents/mock_exam_agent.py` |
| Foundry | `foundry/client.py`, `foundry/synthetic_iq.py`, `foundry/queries.py`, `data/knowledge_base.json` |
| Evaluation | `evaluation/evaluator.py` |
| Tests | `tests/strict_qa_tests.py`, `tests/run_all_tests.py` |
| CLI | `main.py` |

---

## 13. Phase 0 Verdict

**Proceed to Phase 1–18:** Yes, with the above as the fix backlog.

**Demo-safe today?** Partially — Streamlit UI works for `L-*` IDs with valid subjects, but judges who probe reasoning visibility, ID format, career-degree coherence, stale edits, or CLI will find clear rejection hooks.

**Priority fix order (recommended):**
1. `LearnerState` + `PriorityEngine` (Phases 1, 3)
2. Input normalization + relax ID prefix rule (Phase 2)
3. Wire all agents to canonical state (Phases 1, 4)
4. Expose reasoning tab in UI (Phase 13)
5. Remove Physics hardcoding in consensus/counterfactual (Phases 5, 14)
6. Honest evaluation + ConsistencyValidator (Phases 4, 16)
7. UI flow + stale-state invalidation (Phases 11, 12)
8. Fix `main.py` resource crash (Phase 18)

---

*End of Phase 0 rejection audit.*
