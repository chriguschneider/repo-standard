---
name: commit-guardian
description: Before any `git commit` in this repo, verify that staged changes do not contradict an accepted ADR in docs/adr/ or break the conventions in AGENTS.md. Activates when the user says "commit", "commit this", "let's commit", or before running `git commit ...` via Bash. Reports findings as a numbered list referencing ADR number plus file:line, then waits for user confirmation. Non-blocking — the user always decides.
---

# Commit Guardian

Pre-commit ADR and convention check for @@NAME@@. Runs before any
`git commit` to catch violations of accepted decisions in `docs/adr/` and
conventions in [`AGENTS.md`](../../../AGENTS.md).

Complementary to [`documentation-guardian`](../documentation-guardian/SKILL.md):
that one triggers when an architectural change *happens*; this one
triggers when a commit is *imminent*.

## Activation triggers

- About to run `git commit ...` via Bash.
- The user says "commit", "commit this", "let's commit", "ready to commit".

## Skip

- The user opts out ("just commit", "skip the check").
- Trivial diffs with no architectural surface: typo/prose fixes,
  whitespace, comment rewording, a single constant/default tweak.
- A pure version bump for a release commit (that is the required sync).

## Workflow

1. `git diff --staged` and `git status` to see what is actually staged.
2. `git rev-parse --abbrev-ref HEAD`. If it is `@@BRANCH@@`, **stop** and
   offer to create a feature branch (the flow is PR-only).
3. Read every ADR under `docs/adr/` (skip `README.md`, `template.md`) plus
   `AGENTS.md`, unless already in context. Extract checkable rules.
4. Match each finding to a `path:line` in the diff.
5. Output:
   - **All clear:** one line, "All checks pass, proceeding with commit."
   - **Findings:** numbered list, each naming `ADR NNNN` or the convention
     source, the rule, and the offending `path:line`.
6. If anything is flagged, wait for the user. Never block.

## Checkable rules (current)

From AGENTS.md:

- **Version sync** — @@VERSION_SYNC_RULE@@
- @@CHANGELOG_GUARD_RULE@@
- **English only** in code, comments, commit messages.
- **Commit trailer** — an AI-authored commit carries an honest
  `Co-Authored-By:` trailer.
- **No direct commit to `@@BRANCH@@`.**
- **Explaining comments survive** — flag a diff that deletes a comment
  citing an issue (`#123`) or an ADR: those record why odd-looking code is
  the way it is.
- **Generated artifacts in sync** — a change to sources of a committed
  build output (bundle, PDF, generated table) carries the regenerated
  output in the same commit.

From the ADRs: TODO(repo-standard): one bullet per repo-specific ADR with
the rule in checkable form (hosts, paths, imports, budgets).

Do not rely on this list being complete: new ADRs land over time, always
re-read `docs/adr/`.
