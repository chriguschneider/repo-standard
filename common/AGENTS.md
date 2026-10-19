# AGENTS.md

Conventions for AI-assisted contributions to this repo (Claude Code,
Cursor, Codex, Aider, or any other assistant). Read this first if you are
an AI assistant working on a branch, or a human driving one.

---

## Shared Skeleton

These conventions apply across all of @@OWNER@@'s repos and come from
[`repo-standard`](https://github.com/@@OWNER@@/repo-standard). Repo-specific
sections follow below.

### Commit attribution

Commits made with AI assistance carry a `Co-Authored-By:` trailer that
names the tool and model honestly, e.g.:

```
Co-Authored-By: Claude <noreply@anthropic.com>
Co-Authored-By: Codex <noreply@openai.com>
```

The exact string is not load-bearing; what matters is that git history
reflects what did the typing.

### Language

English only in code, comments, commit messages, and these repo docs.
Non-English is fine in chat, but never gets persisted to a file or a
commit.

### Comment discipline

Inline comments earn their place by explaining the *why* (a hidden
constraint, a subtle invariant, a workaround), not by restating the
code. The PR description is the place for context that does not survive
the diff.

### Model selection

Route the model to the difficulty, not the other way round:

- **Haiku** — trivial mechanical: typos, docs, a config default, a bumped
  constant, value validation.
- **Sonnet** — the default: normal bug fixes, tests, CI, well-scoped
  features.
- **Opus** — architectural surface: lifecycle/teardown, concurrency,
  hardening, ambiguous root-cause hunting, anything ADR-worthy.

### Parallel work

- **Branch naming**: `<tool-or-initials>/<issue>-<slug>`, e.g.
  `claude/4-config-flow`.
- **Issue claiming**: `gh issue edit <N> --add-assignee @me` before
  starting, so parallel contributors (and the autopilot) see it is taken.
- **Worktrees**: parallelize along module boundaries, one worktree each:
  `git worktree add ../@@REPO@@-<issue> <branch>`. One file, one lane.

### Draft PRs

CI runs on every push. If you iterate with several pushes, open the PR as
a **draft** until you expect CI to pass, then mark ready. Direct push to
`@@BRANCH@@` is not the flow; open a PR.

### Changelog entries

Every PR that changes user-visible behavior adds an entry to
`CHANGELOG.md` under `## [Unreleased]` in the right subsection
(Added/Changed/Deprecated/Removed/Fixed/Security, per
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)).

**Exemption:** a fix for a feature that never appeared in a released
version needs no entry — it has no user-visible before-state.

The release commit (`chore(release): vX.Y.Z`) renames `## [Unreleased]`
to `## [vX.Y.Z] — YYYY-MM-DD`; the release workflow extracts that section
verbatim as the GitHub release notes.

### Architectural decisions

If a change adds an upstream endpoint or dependency, adds a platform or a
public option, adds a quality gate, or deviates from an existing ADR, it
needs an ADR. Triggers and the template are in
[`docs/adr/README.md`](docs/adr/README.md). Land the ADR with the code.

Claude Code users get automatic prompts via the repo-local skills in
`.claude/skills/`:

- **`commit-guardian`** — before any `git commit`, checks the staged diff
  against accepted ADRs and these conventions. Non-blocking.
- **`documentation-guardian`** — proposes an ADR when an architectural
  change happens and flags changes that contradict an existing decision.

### Automation

Opt-in, draft-PR-only (see [`docs/agent-automation.md`](docs/agent-automation.md)):
add the **`agent:go`** label to hand an issue to Claude, or write
**@claude** in a comment (owner/collaborators only). The model comes from
the issue's labels via `.github/scripts/pick-model.sh`. The agent cannot
modify `.github/workflows/`.

---

## Repo-Specific: @@NAME@@

### What this is

@@DESCRIPTION@@

TODO(repo-standard): two or three sentences on scope and what this repo
deliberately is *not*. Name sibling repos if there are any.

### Repo structure (target)

```
@@STRUCTURE@@
```

The tree above is the plan; the scaffold ships only the skeleton. Issues
fill it in.

### Non-negotiables from the ADRs

TODO(repo-standard): the hard rules every change must respect, each
pointing to its ADR (allowed upstreams, budgets, module boundaries,
attribution). The agent workflows tell the agent to stop rather than
break one of these.

### Release procedure

@@RELEASE_STEPS@@

### Testing

@@TESTING@@
