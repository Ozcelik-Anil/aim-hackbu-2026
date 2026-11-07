# AI assistance and external components

Keep this record accurate as the project develops. This is a working disclosure, not a claim that a final submission has been made.

## Assistance so far

- Codex assisted with problem exploration, finding public sources, and comparing possible prototype scopes.
- Codex prepared the repository README, collaboration guide, ignore rules, pull request template, and this disclosure document.
- The study-site guard branch contains the application and Gemini integration. See its source and tests for the implemented boundary.

## Record future assistance

For each substantial use, record:

- Tool or model and date.
- Purpose: research, implementation, debugging, design, or evaluation.
- Files or components affected.
- What the team reviewed, tested, or changed.

## External components

Record libraries, APIs, datasets, adapted code, and assets actually used, with source links and applicable licenses. Distinguish original team work from reused components.

## Final review

Before submission, replace status statements that are no longer current and ensure the team can explain the architecture, behavior, evaluation, and limitations.

## Streamlit interface work - November 7, 2026

Irmak prepared the AgentGuard interface and three UI regression tests with AI assistance. Codex integrated her handoff with the newer API and validation error handling on the team branch. The automated live-mode tests use mocked Gemini responses.
