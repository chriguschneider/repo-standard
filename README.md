# repo-standard

The scaffold every new repo of mine starts from, and the yardstick older
repos are checked against. Distilled from
[`hass-meteoswiss-weather`](https://github.com/chriguschneider/hass-meteoswiss-weather),
[`hass-meteoswiss-radar`](https://github.com/chriguschneider/hass-meteoswiss-radar)
and [`weather-station-card`](https://github.com/chriguschneider/weather-station-card),
where each piece was learned the hard way.

What a rendered repo gets:

- **Conventions** for humans and AI assistants (`AGENTS.md`), an ADR
  process (`docs/adr/`) and two repo-local Claude Code skills that guard
  commits against it.
- **CI** with the jobs that become required checks, **CodeQL**,
  **Dependabot**, and a **tag-triggered release** that refuses a tag that
  does not match the declared version or has no changelog section.
- **Agent automation**: `agent:go` label or `@claude` comment → draft PR;
  an independent Opus reviewer that auto-merges or holds with
  `needs-verification`; optionally an autopilot that works the P-labelled
  backlog one PR at a time. Everything skips itself until the
  `CLAUDE_CODE_OAUTH_TOKEN` secret exists.

## Layout

```
render.py          render a new repo (stdlib only)
github-setup.py    labels, repo settings, branch protection (via gh)
check.py           compare an existing repo with the standard (read-only)
labels.json        standard labels
common/            files every repo gets
types/<type>/      type-specific files + type.json (placeholders, required checks, labels)
modes/autopilot/   extra files for mode `autopilot`
```

Types: `ha-integration` (Python, HACS zip release), `lovelace-card`
(TypeScript + Lit + Rollup, committed `dist/`).

Modes: `minimal` (label + mention only, for repos without branch
protection), `opt-in` (+ reviewer and auto-merge, the default), `autopilot`
(+ backlog grind).

## Use

```bash
# 1. render
python3 render.py --type ha-integration --mode opt-in \
  --out ~/Projects/hass-foo \
  --set REPO=hass-foo --set "NAME=Foo" --set DOMAIN=foo \
  --set "DESCRIPTION=One sentence on what it does."
# then fill every TODO(repo-standard) it lists and run the `next:` steps

# 2. publish
cd ~/Projects/hass-foo && git init -b master && git add -A && git commit -m "chore: scaffold from repo-standard"
gh repo create chriguschneider/hass-foo --public --source . --push --description "..."

# 3. GitHub side (protection after the first CI run, so the checks exist)
python3 github-setup.py --repo chriguschneider/hass-foo --type ha-integration

# 4. by hand: Claude GitHub App on the repo, then
gh secret set CLAUDE_CODE_OAUTH_TOKEN -R chriguschneider/hass-foo

# check any repo, old or new
python3 check.py ~/Projects/hass-foo --github chriguschneider/hass-foo --vault ~/Projects/athene
```

Placeholders are `@@KEY@@` (not `{{key}}`, which collides with GitHub's
`${{ }}`). `python3 render.py --type <t> --list` shows them.

## Changing the standard

A lesson learned in one repo goes here first, then into the others via
`check.py`. Models are referenced by alias (`opus`, `sonnet`, `haiku`) so
nothing here goes stale with a model release.

## Licence

[MIT](LICENSE)
