<h1 align="center">@@NAME@@</h1>

<p align="center"><strong>@@DESCRIPTION@@</strong></p>

<p align="center">
  <a href="LICENSE"><img alt="License: MIT" src="https://img.shields.io/badge/License-MIT-yellow.svg" /></a>
  @@BADGES@@
  <a href="https://github.com/@@OWNER@@/@@REPO@@/actions/workflows/ci.yml"><img alt="CI status" src="https://img.shields.io/github/actions/workflow/status/@@OWNER@@/@@REPO@@/ci.yml?branch=@@BRANCH@@&label=CI" /></a>
  @@RELEASE_BADGE@@
  <a href="https://github.com/@@OWNER@@/@@REPO@@/commits/@@BRANCH@@"><img alt="Last commit" src="https://img.shields.io/github/last-commit/@@OWNER@@/@@REPO@@" /></a>
  @@FUNDING_BADGE@@
  <a href="#ai-assisted-development"><img alt="AI Assisted" src="https://img.shields.io/badge/AI-assisted-2196F3.svg" /></a>
</p>

<p align="center">
  @@LINKS@@
  <a href="https://github.com/@@OWNER@@/@@REPO@@/issues">Issues</a>
  @@CHANGELOG_LINK@@
</p>

## What it does

TODO(repo-standard): what someone gets from this, in plain words, before
any technical detail.

@@INSTALL@@

## AI-assisted development

Built by @@AUTHOR@@ & Claude, a human and an LLM working together. The
architecture calls and the trade-offs are human; a good share of the
typing, refactors and tests is [Claude Code](https://claude.com/claude-code),
locally and as unattended agents on GitHub (see
[`docs/agent-automation.md`](docs/agent-automation.md)).

AI-assisted commits carry a `Co-Authored-By:` trailer, so the history stays
honest. The badge is there because being upfront about how software gets
made beats pretending otherwise.

@@FUNDING_LINE@@

## Contributing

Issues and PRs are welcome. Conventions for humans and AI assistants are in
[`AGENTS.md`](AGENTS.md), decisions in [`docs/adr/`](docs/adr/). The repo
layout and automation come from [repo-standard](@@STANDARD_URL@@).

## Licence

[MIT](LICENSE)
