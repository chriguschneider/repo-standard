# ADR-0001: Quality gates, release process and agent automation from repo-standard

- **Status:** Accepted
- **Date:** @@DATE@@

## Context

The repos this setup comes from arrived at their CI, release and agent
setup through a series of real incidents (releases tagged against the wrong tree, an agent
PR sitting silently on a failed check, a reviewer blocked by the bot-actor
guard, pushes going out as the wrong bot). [`repo-standard`](@@STANDARD_URL@@) collects those
lessons so a new repo starts with them instead of repeating them.

## Decision

Adopt the standard as rendered on @@DATE@@ (type `@@TYPE@@`, mode
`@@MODE@@`):

- **CI on every push and PR** (`ci.yml`). Its jobs are required status
  checks on `@@BRANCH@@`; the branch is PR-only, `strict` off.
- **Tag-triggered release** (`release.yml`): an annotated `vX.Y.Z` tag
  becomes a GitHub release only if it matches the declared version and
  `CHANGELOG.md` has a non-empty section for it.
- **CodeQL** `security-extended` on push, PR and weekly.
- **Dependabot** weekly for GitHub Actions and the package ecosystem.
- **Agent workflows**: opt-in via `agent:go`, `@claude` for
  owner/collaborators only, an independent Opus reviewer that auto-merges
  or holds with `needs-verification` (not in mode `minimal`), and in mode
  `autopilot` a backlog grind over P-labelled issues, one PR at a time.
  All of them skip themselves while `CLAUDE_CODE_OAUTH_TOKEN` is absent.
- **Agent guardrails**: a tool allowlist (`--permission-mode dontAsk`,
  never `--dangerously-skip-permissions`), deny rules and a path guard hook
  for `.github/` and `.claude/` (`.claude/ci-settings.json`), only trusted
  issue text, harden-runner on every agent job, a reviewer that reads CI
  instead of running PR-controlled code, a deterministic hold for
  sensitive paths, and unfinished work saved to a draft PR.
- **Every action pinned by commit SHA**, updated by Dependabot after a
  cooldown.
- Models are picked by alias (`opus`, `sonnet`, `haiku`), not by pinned
  ID, so the workflows do not go stale with every model release.

## Consequences

- A change to a gate here is either mirrored back into `repo-standard`
  or recorded as a divergence in a new ADR.
- Secrets (`CLAUDE_CODE_OAUTH_TOKEN`, optional `SONAR_TOKEN`) are
  per-repository and set by the owner.
