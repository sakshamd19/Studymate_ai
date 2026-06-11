# Challenge Compliance Notes

This repository is currently a synthetic-data prototype.

## Guardrails

- Use synthetic learner identifiers only, such as `L-1001`, `EMP-001`, or `TEAM-A`.
- Do not enter real names, emails, customer records, employee records, credentials, or other PII.
- Keep `.env` and Streamlit secrets out of source control.
- Treat local mock responses as demo grounding only. Real cited retrieval requires a completed Microsoft Foundry IQ integration.
- Validate generated recommendations before using them in demos or evaluation loops.

## Current Implementation Status

- Multi-agent orchestration: implemented locally in Python.
- Reasoning and multi-step decision flow: implemented with deterministic agents and optional consensus/counterfactual modules.
- Microsoft IQ layer: represented by `FoundryIQClient` and `FoundryQueries`; live Foundry IQ retrieval is not implemented yet.
- Synthetic data: CLI and UI now guide users to use synthetic learner IDs.

## Known Rule Gap

The current app is framed around academic learner planning. The challenge screenshots describe an enterprise learning and certification scenario. For a final submission, rename the domain entities and demo flow around employees, roles, certifications, approved learning content, team capacity, and manager insights.
