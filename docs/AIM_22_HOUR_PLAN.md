# AIM: 22-hour hackathon operating plan

Prepared November 7, 2026. Team: Anıl, Irmak, Emre.

Status: proposed build scope and working schedule for team review. The team has selected an agent action detector; the email scenario and technical choices below are recommendations, not previously approved requirements. No product code has been written as part of this plan.

## 1. Outcome and product definition

Build a small web demo showing an AI email assistant with and without an independent tool-execution guard. The assistant reads synthetic messages and proposes actions. The guard checks the actual operation against a trusted, explicit user permission policy before any simulated side effect occurs.

Working label: AIM Agent Guard. The team name is AIM; the product name can change without delaying implementation.

Target user: a developer giving an LLM tools that can read or modify user data.

Problem: untrusted email content can instruct an agent to take actions outside the real user's authorization. Merely recognizing suspicious words or asking another LLM whether an action is safe is insufficient authorization.

Track: Agentic Development.

Demo promise: show what the agent tried, why a concrete operation was allowed/blocked/held for approval, and whether the simulated harmful side effect actually happened.

Do not claim universal prompt-injection detection, production readiness, a certified security boundary, or an accuracy percentage extrapolated beyond the test set.

## 2. Approaches considered

1. Text-only injection classifier: quick, but classifying a message does not enforce what an agent can do. Not the recommended core.
2. Second LLM as final authorizer: flexible explanations, but it can make errors or be manipulated. Optional explanation only, not the enforcement authority.
3. Structured action guard around one controlled agent: a real LLM proposes tool calls; server code validates exact actions against user permissions. Recommended for a bounded, testable 22-hour demo.

This is an enforcement prototype with detection/explanation, not a general classifier of whether text was written by AI.

## 3. Minimum scope

One application, one synthetic inbox, one model provider (Gemini), and three tools:

- `read_email`: read a specific allowed message.
- `create_draft`: create a local simulated draft; no real mail delivery.
- `send_email`: write a simulated sent-mail event; no network mail delivery.

Trusted permission modes selected through the app:

- Summarize only: allow reads from the selected inbox; deny drafts and sends.
- Draft reply: allow reads plus local draft creation for the selected thread; deny sends.
- Review send: allow reads and drafts; a send is held until a user approves that exact simulated recipient and content.

Email text, LLM arguments, and model confidence cannot broaden permissions. An attacker saying “the user already approved this” is not approval.

All tools go through one server-side dispatcher. Unknown tools, malformed arguments, out-of-scope message IDs, missing policy, expired approval, changed action parameters, and reused approval are rejected. Approval is bound to the current run and exact canonical action and consumed once immediately before the simulated send.

The agent must not hold another tool path that bypasses the guard. No automatic SDK tool execution before authorization. Model explanations cannot override decisions.

## 4. User flow

Select a scenario and permission mode → run the agent → inspect proposed action → compare protected and unprotected outcomes → inspect the synthetic outbox or held approval.

Protected and unprotected modes use the same model settings, input, starting state, and step limit. Since live LLM runs can differ, distinguish live paired runs from replaying one recorded proposal through both dispatchers.

Visible states: permitted, blocked, awaiting approval, executed, model/API error, step limit, and no dangerous action attempted. Do not manufacture an unsafe proposal if the model resists the attack.

No chain-of-thought display. Show actual tool names/arguments, source message excerpts, policy checks, decision reasons, and side effects.

## 5. Technical proposal

- A single Next.js/TypeScript project for UI and server endpoints, avoiding separate frontend/backend deployments.
- Gemini function calling, using the official Google GenAI SDK after a small compatibility check. Select and pin an available function-calling model in the actual account; no assumed model name or price.
- A small validation library for structured inputs, a server-side policy module, and in-memory synthetic state per run.
- Unit/integration tests for the authorization boundary. UI and full-flow smoke checks.
- No database, account creation, real Gmail, multi-agent framework, real payments, shell tool, or browser extension in the minimum build.

Only the team-configured model endpoint is an external destination. Synthetic inbox content only. The API key remains server-side in ignored local environment settings or deployment secrets.

A hosted demo is preferred after local operation is reliable. Local demo plus a clearly labeled recording is the fallback. Replay mode must display “recorded replay”; it must never pretend to be a live API run.

## 6. Work ownership: AI assists all three people

The team stated that everyone will use AI support; assignments are by deliverable, not assumed coding experience.

### Anıl — product, agent integration, evaluation, demo owner

- Maintain the exact user problem, scope, and acceptance checklist.
- Own the Gemini runner, integration contract, and comparison flow, with Codex assistance.
- Prepare the benchmark labels and result report with input from both teammates.
- Own the Devpost story, submission, demo script, and schedule.
- Review Irmak's guard behavior and request Emre's review of integration work.

If integration becomes the bottleneck, freeze the demo/story draft and move Emre onto integration once the UI's minimum flow works. Anıl must not be left as the only person understanding the agent.

### Irmak — permissions and execution guard owner

- Own structured policy rules, input validation, guarded dispatcher, and exact-action approvals.
- Write tests that prove forbidden actions cannot create side effects.
- Own `src/server/guard/`, dispatcher security checks, and `tests/guard/`.
- Explain why the guard blocks a call even if the LLM says it is approved.

### Emre — interface and delivery owner

- Own the inbox/scenario selector, action timeline, comparison and approval views.
- Own `src/app/` and `src/components/` except agreed route-handler files.
- Handle screenshot/video capture, browser checks, and the clean-start/deployment check with Codex assistance.
- Keep the UI usable when the API is slow, unavailable, or returns no action.

### Codex support

Help write and review code, run relevant checks, resolve integration problems, maintain GitHub, and prepare documentation. Each human remains accountable for their assigned output and must be able to explain it.

Each teammate uses their own branch and gives their AI the shared contract before coding. Do not have three AI sessions rewrite the whole repository. One owner edits shared types; changes to that contract are announced to everyone.

## 7. First-hour agreement and file boundaries

Proposed ownership map:

- Shared contract: `src/shared/contracts.ts`, owned initially by Anıl; all agree on changes.
- Policy engine: `src/server/guard/policy.ts`, Irmak.
- Approval store: `src/server/guard/approvals.ts`, Irmak.
- Sole tool dispatcher: `src/server/tools/dispatcher.ts`, Irmak; Anıl integrates through it.
- Gemini agent loop: `src/server/agent/runner.ts`, Anıl.
- Scenario fixtures: `src/server/scenarios/`, Anıl owns labels; teammates contribute examples.
- API boundary: `src/app/api/runs/`, Anıl.
- UI: remaining `src/app/` and `src/components/`, Emre.
- Evaluation: `tests/`, `scripts/evaluate.ts`, Anıl coordinates; Irmak owns guard tests.

Agree on these data structures before parallel work: proposed action, trusted policy, decision with reason code, execution event, and run result. Include a run ID, tool name, validated arguments, action source, decision, and side-effect status. The frontend may propose a policy selection, but it cannot submit an arbitrary allow decision.

First vertical slice: clicking Run produces one read operation, a server-side decision, and one timeline entry. UI mock data can support early work, but acceptance requires the real endpoint.

## 8. Official clock and 22-hour schedule

All times America/New_York. Official hacking window in the supplied guide: Saturday November 7, 13:00 → Sunday November 8, 11:00. This is a fixed event window, not a rolling 22 hours starting when this file is read. If work starts late, compress optional work and preserve testing/submission time.

### 13:00–14:00 — scope, access and contracts (hour 0–1)

- [ ] Team agrees on the email scenario, minimum features, and scope exclusions.
- [ ] All three can access the repository; verify pending invitations and local startup.
- [ ] Confirm Gemini key works through a server-only test, available model, quota, and billing status without exposing the key.
- [ ] Agree on shared types and file ownership.
- [ ] Anıl opens the official Devpost submission once the event link is available and checks event-specific fields/video requirements.

Exit: one-page scope, shared contract, successful API connectivity check. If Gemini access is blocked, resolve it immediately; do not spend hours building UI around an untested API.

### 14:00–16:00 — build the three pieces (hour 1–3)

- [ ] Anıl: real Gemini response and one structured proposed call, capped at three model turns per run.
- [ ] Irmak: read allowed, forbidden send blocked, unknown tool denied, isolated simulated outbox.
- [ ] Emre: scenario selection, action timeline and result states connected to the agreed response shape.

Exit: the application can display a real proposal and its guard decision.

### 16:00–18:00 — first complete flow (hour 3–5)

- [ ] Integrate real runner → guard → simulated tools → UI.
- [ ] Reset state between runs; remove temporary bypass paths.
- [ ] Demonstrate an authorized summary and a denied out-of-scope send.
- [ ] Deploy an early preview if straightforward; otherwise establish reliable local startup.

Exit at 18:00: a complete user flow. If absent, cut draft mode, live animation and hosting work until it exists.

### 18:00–20:00 — protected/unprotected comparison (hour 5–7)

- [ ] Run both modes from identical synthetic initial state.
- [ ] Show actual outbox side effects separately from proposed actions.
- [ ] Implement the exact-action approval flow only after allow/block works.
- [ ] Write the two-minute story and capture a first fallback recording.

Exit: an audience can see the failure, intervention and legitimate task outcome.

### 20:00–22:00 — adversarial and normal cases (hour 7–9)

- [ ] Prepare 10 attack and 10 benign cases, with expected tool permissions fixed before measuring.
- [ ] Cover forged approval, private inbox access, new destination, changed parameters, unknown tool, malformed input and ordinary legitimate drafting/sending.
- [ ] Keep several cases separate from prompt/guard tuning.
- [ ] Seek short feedback from a mentor or another team on clarity, not an invented claim of product validation.

Exit: traceable first result sheet and a concrete bug list. Check organizer announcements for additional required forms; no Saturday 23:59 form deadline has been verified from the supplied PDF.

### 22:00–00:00 — reliability and first measurement (hour 9–11)

- [ ] Fix authorization bypasses before visual polish.
- [ ] Handle API quota errors, timeouts, empty calls, repeated calls and step limits.
- [ ] Freeze benchmark labels and record baseline/protected outcomes with model ID and settings.
- [ ] Save model traces with synthetic content only; redact credentials from logs.

Exit: no known way around the guarded dispatcher in the scoped demo. If approval is unreliable, remove that mode and present allow/block honestly.

### 00:00–04:00 — staggered rest and consolidation (hour 11–15)

Suggested two-hour rest windows: Anıl 00:00–02:00; Emre 01:00–03:00; Irmak 02:00–04:00. There is always at least one teammate available. Handoffs include branch, last passing check, and next task. Adapt to fatigue; do not assume 66 productive person-hours.

- [ ] Awake teammates handle documentation, focused fixes and low-conflict tasks.
- [ ] No architectural rewrite, provider migration or new major feature.

Exit: rested owners, stable checkpoint and updated handoff notes.

### 04:00–06:00 — evaluation and deployment (hour 15–17)

- [ ] Run the frozen evaluation set, including held-out cases.
- [ ] Repeat the key benign/attack demo pair up to three times if quota allows; report the repetitions and variation.
- [ ] Check frontend integration, approval reuse and state isolation.
- [ ] Verify hosted or local start from documented instructions. Make the local backup independent of hosting availability.

Exit: actual results and reproducible run instructions.

### 06:00–08:00 — feature freeze, presentation and evidence (hour 17–19)

- [ ] Freeze new features at 06:00; only fix material failures.
- [ ] Finish README, architecture diagram, scope limitations, AI disclosure and third-party attribution.
- [ ] Record the actual working flow; label live versus recorded evidence.
- [ ] Prepare 90-second, two-minute and five-minute explanations.
- [ ] Every teammate explains their component and one limitation aloud.

Exit: working demo, backup recording, screenshots and complete submission draft.

### 08:00–10:00 — submission and rehearsal (hour 19–21)

- [ ] Confirm actual Devpost fields, selected track, all three contributors, repository URL and demo/video requirements.
- [ ] Submit an initial complete entry by 09:00; verify submitted status, not merely saved project status.
- [ ] Have a teammate open public links in a signed-out/private window and test access.
- [ ] Rehearse a failure-free two-minute demo and concise Q&A.

Exit: submitted entry and verified links before the deadline.

### 10:00–11:00 — buffer and final verification (hour 21–22)

- [ ] Critical corrections only. Recheck submission status after edits.
- [ ] Preserve the final tested revision and backup media.
- [ ] Stop hacking and complete submission by the official 11:00 deadline.

Afterward: required judging expo 11:30–14:30. Confirm table assignment with organizers. Do not rely on the general MLH suggested demo length as HackBU's official length.

## 9. Evaluation that supports our claim

Use a small labeled test suite, not a claim to reproduce WASP or ART. Those papers inspire the threat model and measurement; their published percentages are not our results.

- Guard correctness: forbidden calls executed / forbidden calls proposed, plus raw counts. A timeout is not a successful block.
- End-to-end harm: attack runs that actually modify the synthetic outbox or disclose an out-of-scope resource / all attack runs. Report attempts separately.
- Utility: benign tasks completed correctly / benign tasks attempted.
- False intervention: benign intended actions blocked or unnecessarily held / benign intended actions evaluated.
- Extra latency: time spent in guard validation, separately from LLM time; show sample count and median if meaningful.
- Trace integrity: every executed call has a corresponding decision on the same run and exact arguments.

Suggested suite: 10 attack + 10 benign cases, paired protected/unprotected runs. With three model calls maximum per run, the first 40 runs have a ceiling of 120 model calls. Check actual quota before running; use a smaller disclosed suite if necessary. No spending limit is inferred from the presence of an API key. Do not enable paid billing or purchase services without explicit authorization.

If the baseline resists an attack, report “not attempted” or “resisted”; do not weaken it secretly. A separate labeled replay can test guard behavior on a known structured dangerous proposal. Do not count replay proposals as live-model failures.

Model settings, scenario IDs, actual decisions, failures and repetitions travel with every result. Hold off on headline percentages until denominators are known.

## 10. Critical test cases

- Read allowed selected message → allowed, no sent event.
- Send while summarize-only → denied, no sent event.
- Create allowed draft → draft exists, no sent event.
- Send needing approval → pending, no sent event until exact user approval.
- Change recipient/content after approval → reject old approval.
- Reuse approval or submit concurrently → at most one simulated send.
- Email claims admin permission/user approval → no policy change.
- Request another run's message or approval → deny.
- Unknown tool, malformed arguments, missing policy → deny without execution.
- Benign legitimate task → completes; blanket blocking does not pass utility.
- API 429/timeout → explicit error state, not a green safety result.
- Model emits no dangerous call → show that honestly, no fabricated red event.
- Reset/new run → no previous inbox/outbox/approval leakage.
- Render hostile message text as text; no executable HTML or injected UI.

## 11. Team rhythm and GitHub

- Ten-minute checkpoint every two hours: show working behavior, current blocker and next deliverable.
- After 20–30 minutes blocked, ask another owner/Codex for help and consider the documented scope cut.
- Branches: `feature/agent-runner`, `feature/action-guard`, `feature/demo-ui`, `test/evaluation`, `docs/submission`.
- One small PR per deliverable, one teammate review, then integration. The owner may bypass protection only deliberately for an urgent, understood fix; document that decision.
- Do not merge unrun AI output. Review the diff and run relevant checks.
- No permanent personal branches or simultaneous edits to shared contracts.
- The three humans decide scope; Codex assists implementation and checks without inventing progress.

## 12. Two-minute demo outline

0:00–0:20: a developer asks an assistant to summarize an inbox; an email must not gain the user's authority.

0:20–0:50: demonstrate the malicious message and an actual unsafe baseline attempt, if observed. Otherwise clearly use a recorded baseline run.

0:50–1:20: show the protected tool decision and unchanged synthetic outbox; reveal the exact violated permission.

1:20–1:40: show a legitimate task still working, and approval if included.

1:40–2:00: show measured counts, bounded scope and future integration direction.

Anıl narrates; Emre drives the UI; Irmak explains the independent authorization boundary during questions. Everyone should be able to substitute for another teammate.

## 13. What research changes in the plan

- WASP distinguishes intermediate agent diversion, actual attacker-goal completion and legitimate-task utility. We measure attempted action, real simulated side effect and benign completion separately. [WASP §3.4](https://arxiv.org/html/2504.18575v3)
- ART studies deployment policy violations with simulated tools. It motivates checking tool operations rather than only offensive text; our small suite is not an ART evaluation. [NeurIPS paper](https://proceedings.neurips.cc/paper_files/paper/2025/file/73368bc7644c054b5bcc6490a8f2fb1c-Paper-Datasets_and_Benchmarks_Track.pdf)
- OWASP recommends authorization outside agent context, least privilege and exact, single-use approvals. These are core design constraints, not claimed originality. [OWASP AI Agent Security](https://cheatsheetseries.owasp.org/cheatsheets/AI_Agent_Security_Cheat_Sheet.html)
- Gemini function calling supplies structured proposed operations; application code controls execution. Validate the active model and account limits before integration. [Function calling](https://ai.google.dev/gemini-api/docs/function-calling) · [Rate limits](https://ai.google.dev/gemini-api/docs/rate-limits)
- MLH recommends a short demo of working behavior; this is general guidance, not an extra HackBU rule. [MLH judging guidance](https://raw.githubusercontent.com/MLH/mlh-hackathon-organizer-guide/master/general-information/judging-and-submissions/judging-plan.md)
- Devpost encourages starting the submission early and checking project-specific requirements. [Submission steps](https://help.devpost.com/article/126-know-your-submission-steps)
- Event times, public source requirement, AI disclosure and judging obligations come from the supplied NYCAIRR X HackBU Hacker Guide. Check newer organizer announcements before final submission.

## Immediate next checkpoint

Agree on the bounded email demonstration and this ownership split. Then implement only the first vertical slice: a genuine Gemini tool proposal, a deterministic server-side decision, and one visible timeline event.
