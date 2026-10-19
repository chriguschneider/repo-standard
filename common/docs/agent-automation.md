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
- **Only trusted issue text is worked.** The issue becomes the agent's
  instructions, so an issue written by someone without write access is
  refused with a comment (and the label removed). Restate the task in your
  own issue, or add `agent:untrusted-ok` after reading the text yourself.

## On @claude mention (`claude-mention.yml`)

Write `@claude ...` in an issue or PR comment. Gated to the owner /
collaborators: comment events carry secrets even from strangers. Only the
owner's and the agent's own comments reach the prompt
(`include_comments_by_actor`).

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

The agent reads text written by others (issues, comments, PR titles, code)
and runs with write access. Every public attack on agent workflows in
2025/26 combined exactly that with an unrestricted shell. So the shell is
restricted, and several layers hold even if the model is talked into
something:

| Layer | What it does | Where |
|---|---|---|
| Tool allowlist | `--permission-mode dontAsk` plus `--allowedTools`: git, a few `gh` subcommands and the repo's own check commands. Anything else is refused without a prompt. No `--dangerously-skip-permissions`. | `claude_args` in each workflow |
| Deny rules | `gh api`, `gh secret`, `gh workflow`, `gh repo`, `curl`, `wget`, force pushes. Deny always wins. | `.claude/ci-settings.json` |
| Path guard hook | Blocks every write to `.github/` and `.claude/`, through file tools or the shell. Runs only on GitHub Actions; local sessions are unaffected. | `.claude/hooks/protect-paths.py` |
| Trusted text only | Untrusted issues are refused, foreign comments are filtered out, the autopilot only takes issues written by the owner. | job `if:`, `include_comments_by_actor`, `pick-next-issue.sh` |
| Egress | harden-runner logs (mode `audit`) or blocks (mode `block`) outbound connections. | first step of each agent job |
| Pinned actions | Every `uses:` is a full commit SHA; Dependabot bumps it after a 7-day cooldown (not for claude-code-action, whose updates are security fixes). | all workflows, `dependabot.yml` |
| Reviewer reads CI | The reviewer never runs the PR's tests or scripts (the PR could change them, and the job holds secrets); CI runs them without secrets. | `claude-review.yml` |
| Sensitive paths | A PR touching `.github/`, `.claude/`, `scripts/`, `docs/adr/`, `AGENTS.md` or dependency files is never auto-merged, whatever the model decided. | last steps of `claude-review.yml` |

The action restores `.claude/` from the base branch on pull requests, so a
PR cannot switch off the settings or the hook.

**About the `workflows` permission:** the official Claude GitHub App is
installed with Workflows read/write, and a token obtained in a January 2026
attack (CVE-2025-66032) carried that permission. In earlier runs of this
setup a push to `.github/workflows/` was rejected with 403, but that is not
a guarantee. The hook above is the boundary that does not depend on how
the token is scoped.

**Switching egress to `block`:** after a few agent runs, open a run's
harden-runner insights (link in the job summary), compare the endpoints
with `allowed-endpoints`, add what is missing, then set
`egress-policy: block` in the agent workflows (or render with
`--set EGRESS_POLICY=block`).

Other rules:

- The prompts tell the agent to follow `AGENTS.md` and `docs/adr/`, to treat
  issue text as a description of a change rather than instructions, and to
  stop rather than guess.
- Ambiguous issue → draft with a "Blocked / needs decision" note.
- **Runs are capped** at 100 turns (mention: 60) and 60 minutes. The agent
  is told to push early and open the draft PR after its first commit. If a
  run still ends early, `save-wip.sh` commits and pushes what is left and
  opens or updates a draft PR labelled **`agent:needs-continuation`**. That
  push uses the workflow token, so it triggers neither CI nor the reviewer:
  unfinished work is never auto-merged. Continue with `@claude continue`,
  or by hand. Still: cut issues small. An issue that needs measurement, an
  ADR and code is three issues, not one.

## Automated review + auto-merge (`claude-review.yml`)

An **independent Opus reviewer** runs on every agent PR (`claude/*`). It
first waits for the required checks, then reviews the diff adversarially
against `AGENTS.md` and the ADRs, reads the CI result (it does not run the
checks itself), fixes substantive problems on the branch (**at most 3
rounds**; CI re-runs on its pushes), then either:

- **auto-merges** (`gh pr merge --auto --squash`) when green and solid, or
- **holds for you** when the change needs a human decision or a live
  check, when the PR or its issue carries **`needs-verification`**, or when
  it could not make the change solid — it labels the PR
  `needs-verification` and comments exactly what to check.

Whatever the model decided, a PR that touches sensitive paths is then held
with `needs-verification`. After that the job waits for the required
checks; if one fails
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
