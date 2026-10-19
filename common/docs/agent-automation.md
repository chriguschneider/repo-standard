# Agent automation (opt-in)

Claude works an issue **only when you hand it over** (or, in autopilot
mode, when it takes the next P-labelled issue). All flows open **draft PRs
only** and never push to the default branch. Every workflow skips itself
with a notice while the `CLAUDE_CODE_OAUTH_TOKEN` secret is missing, so a
fresh setup is never red.

This repo runs in mode **`@@MODE@@`**:

| Mode | Label + mention | Reviewer + auto-merge | Autopilot |
|---|:-:|:-:|:-:|
| `minimal` | ✓ | – | – |
| `opt-in` | ✓ | ✓ | – |
| `autopilot` | ✓ | ✓ | ✓ |

## Opt-in by label (`claude-labeled.yml`)

Add the **`agent:go`** label to an issue → Claude implements it on a
`claude/<n>-<slug>` branch and opens a draft PR. Issues without the label
are never touched by this flow.

- `gh issue edit <n> --add-label agent:go` (or add it in the UI).
- Manually: Actions → "Claude (opt-in via label)" → Run workflow → issue number.
- On failure the `agent:go` label is removed so it isn't left looking claimed.

## On @claude mention (`claude-mention.yml`)

Write `@claude ...` in an issue or PR comment. Gated to the owner /
collaborators: comment events carry secrets even from strangers.

## Model per issue

`.github/scripts/pick-model.sh` chooses the model from labels. It passes
aliases, so the latest model of each family is used without edits here.

| Label | Model |
|---|---|
| `agent:opus` | `opus` |
| `agent:haiku` | `haiku` |
| `agent:sonnet` / (none) | `sonnet` |
| `P1` | `opus` |
| `P3` / `good first issue` | `haiku` |

## Guardrails

- The agent **cannot change `.github/workflows/`** (the app token lacks the
  `workflows` permission). It documents such changes for a human instead.
- The prompts tell the agent to follow `AGENTS.md` and `docs/adr/`, and to
  stop rather than guess.
- Ambiguous issue → draft with a "Blocked / needs decision" note.
- Implementation runs are capped at **150 turns**. A run that hits the cap
  leaves nothing behind, so cut issues small: an issue that needs
  measurement, an ADR and code is three issues, not one.

## Automated review + auto-merge (`claude-review.yml`)

An **independent Opus reviewer** runs on every agent PR (`claude/*`). It
reviews adversarially, runs the checks, fixes substantive problems on the
branch (**at most 3 rounds**), then either:

- **auto-merges** (`gh pr merge --auto --squash`) when green and solid, or
- **holds for you** when the change needs a human decision or a live
  check, when the PR or its issue carries **`needs-verification`**, or when
  it could not make the change solid — it labels the PR
  `needs-verification` and comments exactly what to check.

After its verdict the job waits for the required checks; if one fails
after auto-merge was armed, the PR gets `needs-verification` and a comment
naming the check, instead of sitting silently.

Auto-merge needs branch protection with required checks on
`@@BRANCH@@`. Without it (private repo on a free plan) use mode `minimal`.

## Autopilot (`claude-autopilot.yml`, mode `autopilot` only)

After every closed PR, completed CI/review run, issue label change and on
a cron at :13/:43 — **if no agent PR is open** — it takes the next open
P-issue (P1 before P2 before P3, lowest number first). Skips issues whose
title starts with `Tracking:`, anything assigned, and anything labelled
`agent:go`, `agent:in-progress` or `needs-verification`. Pause it by
disabling the workflow; kick it with `gh workflow run claude-autopilot.yml`.

Give an issue a P-label only when its prerequisites are merged, or the
agent will hit a missing dependency and open a "Blocked" draft.

## Setup (one-time, by the owner)

1. Install the Claude GitHub App on this repository
   (https://github.com/apps/claude), or extend the existing installation
   under https://github.com/settings/installations.
2. `gh secret set CLAUDE_CODE_OAUTH_TOKEN -R @@OWNER@@/@@REPO@@`
   (token from `claude setup-token`; never paste it into a chat).
3. Optional: SonarCloud project + `SONAR_TOKEN`.
