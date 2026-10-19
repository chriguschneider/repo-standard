<h1 align="center">@@NAME@@</h1>

<p align="center"><strong>@@DESCRIPTION@@</strong></p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" /></a>
  <a href="https://hacs.xyz/"><img alt="HACS Custom" src="https://img.shields.io/badge/HACS-Custom-orange.svg" /></a>
  <a href="https://github.com/@@OWNER@@/@@REPO@@/releases/latest"><img alt="Latest release" src="https://img.shields.io/github/v/release/@@OWNER@@/@@REPO@@" /></a>
  <a href="https://github.com/@@OWNER@@/@@REPO@@/actions/workflows/ci.yml"><img alt="CI status" src="https://img.shields.io/github/actions/workflow/status/@@OWNER@@/@@REPO@@/ci.yml?branch=@@BRANCH@@&label=CI" /></a>
  <a href="https://github.com/@@OWNER@@/@@REPO@@/releases"><img alt="Downloads" src="https://img.shields.io/github/downloads/@@OWNER@@/@@REPO@@/total" /></a>
  <a href="https://github.com/@@OWNER@@/@@REPO@@/stargazers"><img alt="Stars" src="https://img.shields.io/github/stars/@@OWNER@@/@@REPO@@?style=flat&label=stars" /></a>
  <a href="https://github.com/@@OWNER@@/@@REPO@@/commits/@@BRANCH@@"><img alt="Last commit" src="https://img.shields.io/github/last-commit/@@OWNER@@/@@REPO@@" /></a>
  <a href="https://buymeacoffee.com/chriguschneider"><img alt="Buy Me a Coffee" src="https://img.shields.io/badge/Buy%20Me%20a%20Coffee-support-FFDD00.svg" /></a>
  <a href="#ai-assisted-development"><img alt="AI Assisted" src="https://img.shields.io/badge/AI-assisted-2196F3.svg" /></a>
</p>

<p align="center">
  <a href="https://my.home-assistant.io/redirect/hacs_repository/?owner=@@OWNER@@&repository=@@REPO@@&category=plugin"><img src="https://my.home-assistant.io/badges/hacs_repository.svg" alt="Open in HACS" /></a>
  &nbsp;·&nbsp;
  <a href="https://github.com/@@OWNER@@/@@REPO@@/issues">Issues</a>
  &nbsp;·&nbsp;
  <a href="CHANGELOG.md">Changelog</a>
</p>

## What it does

TODO(repo-standard): what a user gets after installing it, in plain words,
before any technical detail.

## Installation

### HACS (recommended)

1. Click **Open in HACS** above, or in HACS → ⋮ → *Custom repositories* add
   `https://github.com/@@OWNER@@/@@REPO@@` as type *Dashboard*.
2. Download **@@NAME@@**. HACS registers the resource for you.
3. Edit a dashboard → **Add card** → *@@NAME@@*.

### Manual

Copy `dist/@@DOMAIN@@.js` to `config/www/` and add it as a resource
(`/local/@@DOMAIN@@.js`, type *JavaScript module*).

## Configuration

```yaml
type: custom:@@DOMAIN@@
title: @@NAME@@
```

TODO(repo-standard): all options with defaults.

## AI-assisted development

Built by Chrigu & Claude, a human and an LLM working together. The
architecture calls and the trade-offs are mine; a good share of the
typing, refactors and tests is [Claude Code](https://claude.com/claude-code),
on my machine and as unattended agents on GitHub (see
[`docs/agent-automation.md`](docs/agent-automation.md)).

AI-assisted commits carry a `Co-Authored-By:` trailer, so the history stays
honest. The badge is there because being upfront about how software gets
made beats pretending otherwise.

If this card earned a place on your dashboard,
[a coffee](https://buymeacoffee.com/chriguschneider) is a nice way to say
thanks. (Claude doesn't drink coffee. More for me.)

## Contributing

Issues and PRs are welcome. Conventions for humans and AI assistants are in
[`AGENTS.md`](AGENTS.md), decisions in [`docs/adr/`](docs/adr/).

## Licence

[MIT](LICENSE)
