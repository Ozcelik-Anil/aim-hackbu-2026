# AIM | HackBU 2026

Team workspace for the NYCAIRR AI Responsibility Hackathon, November 7–8, 2026.

**Team AIM:** Anil ([@Ozcelik-Anil](https://github.com/Ozcelik-Anil)), Irmak ([@kidikirmak2204-crypto](https://github.com/kidikirmak2204-crypto)), Emre ([@emrecan-aycil](https://github.com/emrecan-aycil)).

## Project status

AgentGuard starts with a research question. Gemini plans up to two searches, and the app retrieves up to six article introductions or abstracts from Wikipedia and Crossref. A guard inspects each excerpt before synthesis. Flagged, failed, or empty extractions cannot supply evidence. The report links its findings to the checked sources. The separate Source Inspector page retains the manual inspection demo and its recorded evaluation.

## Working together

1. Keep `main` ready for the demo.
2. Create a short-lived branch for each task, such as `feature/offer-input`, `fix/source-links`, or `docs/demo-script`.
3. Open a pull request with the change, how it was checked, and any known limits. Ask another teammate to review when possible.
4. Merge small changes frequently. Pull the latest `main` before starting the next task.
5. Track concrete tasks in GitHub Issues and agree on one owner per task.

Read [CONTRIBUTING.md](CONTRIBUTING.md) for the short team guide.

## Responsible AI

- Show evidence for claims and make uncertainty visible.
- Use synthetic or appropriately redacted demonstration data.
- Keep API keys, credentials, and private user data out of the repository.
- Record AI assistance and external components in [docs/AI_USAGE.md](docs/AI_USAGE.md).

## Run locally

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m streamlit run app.py
```

Open the local URL printed by Streamlit. On Windows, activate with
`.venv\Scripts\Activate.ps1` in PowerShell.

### Offline sample

Open Source Inspector in the sidebar for the sample and the recorded six-case evaluation. The research homepage requires live Gemini access.

Select **Offline example**, then click **Load Sample Study Site with Trap**.
One click fetches a fictional page from a temporary loopback HTTP server and
shows its prerecorded four-field verdict. This mode needs no API key and does
not run a model. The lesson remains visible; the credential request is excluded
from the extracted notes. Expand the permission simulation to verify that form
submission is denied. No credentials are collected or transmitted by the simulation.

### Live Gemini

Set `GEMINI_API_KEY` in your server environment before launching Streamlit.
Alternatively, the local research homepage accepts a key in its masked session field.
The optional backup connection accepts a second authorized Gemini key here or via
`GEMINI_BACKUP_API_KEY`. On HTTP 429 the research run retries the same step once
with the backup and uses it for the rest of the run. Keys in one project share quota.
Ask a question and choose **Start research**. Keep keys out of source files and commits.
To inspect an individual sample instead, open **Source Inspector**, select **Live Gemini**, then
load the sample or edit the page and click **Inspect page**. Only fictional page
text should be sent. The backend controls the model configuration in `guard.py`.

Results are reused on reruns only while the page and mode match. Editing either
hides the result until another inspection. Inspection failures clear previous
notes and JSON and show a generic error without SDK exception details.

### Verification

```bash
python -m unittest discover -v
```

Nine tests cover quota failover, guarded research evidence and citations, response validation, clean and threat display, note extraction,
permission denial, changed inputs, failed inspections, failed sample loading,
plain-text display and avoiding repeated live calls on reruns.

The model's clean verdict is not a safety guarantee. This demo only permits local
note display; it does not implement general-purpose web-agent protection. Offline
playback and mocked live tests do not establish live Gemini detection accuracy.

## Submission

Use [docs/SUBMISSION.md](docs/SUBMISSION.md) to track the public source link, reproducible demo, evaluation, and AI disclosure.
