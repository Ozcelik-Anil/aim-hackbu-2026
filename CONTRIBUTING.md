# Team collaboration guide

Team AIM: Anil, Irmak and Emre. Use your own GitHub account.

## Access

Accept the repository collaborator invitation before pushing a branch. A pending invitation does not grant write access. Repository permissions and an AI tool's GitHub connection are separate: an assistant may read a public repository while lacking branch, commit or pull-request tools.

If the assistant cannot publish a change, provide the changed files or a patch and verification notes for integration. Attribute the teammate's contribution in the pull request. Keep credentials out of handoffs.

## Each task

1. Pull the latest `main` and create a focused branch, for example `fix/guard-retry` or `docs/demo-script`.
2. Coordinate ownership before changing a shared file.
3. Use English prose and ASCII names for files, branches and commits.
4. Run the relevant checks using the README instructions.
5. Open a pull request into `main` describing the user-visible behavior, verification and any remaining limitations.
6. Ask a teammate to review, then merge a small, tested change.

Preserve shared history. Include only relevant files in each commit.

## Credentials and data

Configure team keys through server environment variables or `.streamlit/secrets.toml`. The app does not load `.env` files automatically. The secrets file is ignored by Git and must also be omitted from shared archives.

Use fictional attack examples. Check screenshots and staged files before publishing. An ignore rule does not remove a file that was already committed.

## Review focus

A source inspection failure must never become a clean verdict. Only checked evidence may reach synthesis. Output must stay safe to display, and partial results must remain visibly labeled. Keep the two-source budget and documented model settings consistent with the implementation.

Record substantial AI assistance and externally sourced components in [docs/AI_USAGE.md](docs/AI_USAGE.md). Keep claims about the recorded evaluation tied to its cases and guard revision.
