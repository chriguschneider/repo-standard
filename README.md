# repo-standard

[![Self-test](https://github.com/chriguschneider/repo-standard/actions/workflows/selftest.yml/badge.svg)](https://github.com/chriguschneider/repo-standard/actions/workflows/selftest.yml)

How I set up a GitHub repo so Claude agents can work on it: conventions,
decisions, CI, releases and the agent automation, as a scaffold you can
render for a new repo and a check you can run against an old one.

Read [**How it works**](docs/how-it-works.md) for the loop (issue → agent →
draft PR → independent reviewer → auto-merge or human), the model routing,
and the table of incidents that turned into guards.

Distilled from
[`hass-meteoswiss-weather`](https://github.com/chriguschneider/hass-meteoswiss-weather),
[`hass-meteoswiss-radar`](https://github.com/chriguschneider/hass-meteoswiss-radar)
and [`weather-station-card`](https://github.com/chriguschneider/weather-station-card).

## What a rendered repo gets

- **Conventions** for humans and AI assistants (`AGENTS.md`), an ADR process
  (`docs/adr/`) and two repo-local Claude Code skills that guard commits
  against it.
- **CI** whose jobs become the required checks, **CodeQL**, **Dependabot**,
  and a **tag-triggered release** that refuses a tag that does not match the
  declared version or has no changelog section.
- **Agent automation**: `agent:go` label or `@claude` comment → draft PR; an
  independent Opus reviewer that auto-merges or holds with
  `needs-verification`; optionally an autopilot that works the P-labelled
  backlog one PR at a time. Everything skips itself until the
  `CLAUDE_CODE_OAUTH_TOKEN` secret exists.
- **Guardrails** for agents that read untrusted text: a tool allowlist
  instead of `--dangerously-skip-permissions`, a hook that blocks writes to
  `.github/` and `.claude/`, egress control, SHA-pinned actions, a reviewer
  that reads CI instead of running PR code, and unfinished runs saved to a
  draft PR. zizmor and actionlint check every rendered type.

## Types and modes

| Type | For | Checks |
|---|---|---|
| `generic` | anything without its own toolchain yet: config, scripts, docs | `scripts/check.sh` (grows with the repo) |
| `python` | a Python package or command-line tool | ruff, pytest; release attaches sdist + wheel |
| `ha-integration` | a Home Assistant custom integration (HACS) | hassfest, HACS, ruff, pytest; zip release |
| `lovelace-card` | a Home Assistant dashboard card (HACS) | HACS, eslint, tsc, vitest, build; committed `dist/` |

| Mode | Label + `@claude` | Reviewer + auto-merge | Autopilot |
|---|:-:|:-:|:-:|
| `minimal` — no branch protection (e.g. private repo on a free plan) | ✓ | – | – |
| `opt-in` — the default | ✓ | ✓ | – |
| `autopilot` — an ordered backlog to clear | ✓ | ✓ | ✓ |

## Use it yourself

You need: `git`, Python 3.12+, the [`gh` CLI](https://cli.github.com/)
logged in, a Claude subscription (for the agent token) and the
[Claude GitHub App](https://github.com/apps/claude). Docker and Node only for
the type that needs them.

```bash
git clone https://github.com/chriguschneider/repo-standard.git
cd repo-standard

# optional, once: your identity and an optional funding link
mkdir -p ~/.config/repo-standard
cat > ~/.config/repo-standard/defaults.json <<'EOF'
{"OWNER": "your-github-login", "AUTHOR": "Your Name", "FUNDING_URL": ""}
EOF
# without it, OWNER comes from `gh api user` and AUTHOR from `git config user.name`

# 1. render (see the placeholders with --list)
python3 render.py --type python --mode opt-in --out ~/code/my-tool \
  --set REPO=my-tool --set "NAME=My Tool" --set DOMAIN=my_tool \
  --set "DESCRIPTION=One sentence on what it does."
# fill every TODO(repo-standard) it lists, run the `next:` steps

# 2. publish
cd ~/code/my-tool && git init -b master && git add -A
git commit -m "chore: scaffold from repo-standard"
gh repo create <owner>/my-tool --public --source . --push

# 3. GitHub side: labels and settings now, branch protection after the
#    first CI run (the check names must exist)
python3 ../repo-standard/github-setup.py --repo <owner>/my-tool --type python --only labels,settings
python3 ../repo-standard/github-setup.py --repo <owner>/my-tool --type python --only protection

# 4. by hand: install the Claude GitHub App on the repo, then
claude setup-token   # copy the token, never paste it into a chat
gh secret set CLAUDE_CODE_OAUTH_TOKEN -R <owner>/my-tool

# check any repo, new or old, against the standard
python3 check.py ~/code/my-tool --github <owner>/my-tool
```

This is not a GitHub "template repository" on purpose: the files need the
placeholders filled and the type and mode chosen, which `render.py` does.

## Layout

```
render.py          render a new repo (stdlib only)
github-setup.py    labels, repo settings, branch protection (via gh)
check.py           compare an existing repo with the standard (read-only)
labels.json        standard labels
common/            files every repo gets
types/<type>/      type-specific files, type.json, _snippets/ for the README
modes/autopilot/   extra files for mode `autopilot`
docs/              how it works
```

Placeholders are `@@KEY@@` (not `{{key}}`, which collides with GitHub's
`${{ }}`). A new type is a folder under `types/` with a `type.json`; copy the
closest existing one.

## Status

A personal standard, used on my own repos and shared because the set-up is
the interesting part. Issues and ideas are welcome; there is no support
promise. Every push renders all four types and runs their checks (badge above);
the GitHub side has been proven in the repos it was distilled from.

## Licence

[MIT](LICENSE)
