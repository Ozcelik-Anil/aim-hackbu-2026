# Team collaboration guide

## First-time access

The repository link lets everyone view a public project. To push changes, accept the collaborator invitation sent to your GitHub account. Each teammate should use their own account.

Clone this repository after accepting the invitation. Never share passwords, access tokens, or API keys with teammates through commits or issues.

## Each task

1. Update your local `main`.
2. Create a branch named `feature/<task>`, `fix/<task>`, or `docs/<task>`.
3. Agree on file ownership when two tasks touch the same area.
4. Make focused commits with meaningful messages.
5. Push your branch and open a pull request into `main`.
6. Explain what changed and what you checked. Include a screenshot for visible UI changes when useful.
7. Request a teammate review. Merge after the relevant checks pass.

Do not force-push `main` or rewrite shared history. If there is a conflict, coordinate with the person editing that area before resolving it.

## Secrets and demonstration data

- Store local keys in ignored `.env` files. Share only variable names in `.env.example` once the application needs them.
- Do not commit real emails, financial records, identification documents, raw inbox exports, or unredacted screenshots.
- Clearly label synthetic examples. Do not present generated examples as real victim reports.
- Ignore rules do not remove files already tracked by Git. Review the staged changes before every commit.

## Quality bar

The app should start using the README instructions. Test the actual user flow, include uncertainty and failure states, and describe limitations honestly. Record AI assistance in `docs/AI_USAGE.md` as work progresses.

## Roles

Team members: Anıl, Irmak, Emre. Responsibilities will be assigned after the project is selected; no technical role is assumed yet.
