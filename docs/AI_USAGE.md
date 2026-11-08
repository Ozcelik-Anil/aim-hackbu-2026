# AI assistance and external components

## Team work and AI assistance

Team AIM selected the research-assistant security problem, reviewed scope changes, supplied Gemini access, and prepared the hackathon deliverable with AI assistance.

Codex assisted with source research, repository setup, the Python guard, automated retrieval and synthesis, Streamlit interfaces, quota handling, regression tests and documentation. The team is responsible for understanding the implementation and reviewing the final claims.

Irmak supplied the interface handoff and UI tests with AI assistance. A second supplied handoff defined the six paired evaluation cases and scoring instructions. Codex integrated these files and ran the first recorded live evaluation. The GitHub integration commits were made through Anil's connected account.

The exact models used by teammates' separate chats were not independently verified.

## Runtime model

The application uses Google's Gemini API through the Google GenAI Python SDK. The configured model is `gemini-3.5-flash`, with low thinking, for search planning, source inspection and report synthesis. Team credentials are resolved on the server.

The original six-case evaluation and subsequent live connectivity checks used real API calls. Automated regression tests mock model responses. Later guard instructions evolved, so the original evaluation record identifies the earlier guard revision.

## External software and source services

Direct dependencies are declared in [requirements.txt](../requirements.txt):

- [Streamlit](https://github.com/streamlit/streamlit) - application framework, Apache-2.0.
- [Google GenAI Python SDK](https://github.com/googleapis/python-genai) - model API client, Apache-2.0.
- [Pydantic](https://github.com/pydantic/pydantic) - structured response validation, MIT.
- [Requests](https://github.com/psf/requests) - HTTP client, Apache-2.0.

Live retrieval uses the [Wikipedia API](https://www.mediawiki.org/wiki/API:Main_page) and [Crossref REST API](https://www.crossref.org/documentation/retrieve-metadata/rest-api/). Their source records and linked publications retain their own content licenses. Source links in research reports provide attribution; software dependency licenses do not grant rights to third-party research text.

## Research that informed the problem

[WASP](https://arxiv.org/abs/2504.18575) and [Security Challenges in AI Agent Deployment](https://proceedings.neurips.cc/paper_files/paper/2025/hash/73368bc7644c054b5bcc6490a8f2fb1c-Abstract-Datasets_and_Benchmarks_Track.html) informed the threat model. The six fictional scenarios are a small team-prepared evaluation. The project does not reproduce either paper's benchmark or inherit its reported results.

## Verification and delivery

Ten automated tests passed at the documentation update. The recorded six-case live detector run is in [evals/live_run.json](../evals/live_run.json), with scoring guidance in [evals/README.md](../evals/README.md).

One earlier question-first live research run completed. Later runs encountered HTTP 429 and motivated failover and partial-output handling. The final two-source configuration has automated coverage; a final successful live rehearsal and Devpost submission remain to be confirmed by the team.

## Research audit update - November 8, 2026

Codex added per-source inspected excerpts and validated guard verdicts, displayed
them in plain-text Streamlit widgets, and added four regression tests for evidence
integrity, rerun behavior, failed research and unavailable guard verdicts. All 14
tests passed locally with mocked model/provider calls. No new live Gemini run
or public deployment was performed for this update. Local-only delivery remains
the team requirement.
