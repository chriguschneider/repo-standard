#!/usr/bin/env bash
# Every check CI and the agents run. Extend it as the repo grows (linters,
# tests, a build) instead of adding CI jobs, so a local run equals CI.
set -euo pipefail
cd "$(dirname "$0")/.."

fail() { echo "::error::$*" >&2; exit 1; }

version="$(tr -d '[:space:]' < VERSION)"
[[ "$version" =~ ^[0-9]+\.[0-9]+\.[0-9]+(-[0-9A-Za-z.]+)?$ ]] || fail "VERSION '$version' is not semver"
grep -q '^## \[Unreleased\]' CHANGELOG.md || fail "CHANGELOG.md has no '## [Unreleased]' section"
grep -q "^## \[v$version\]" CHANGELOG.md || fail "CHANGELOG.md has no '## [v$version]' section"
grep -q "^\[v$version\]:" CHANGELOG.md || fail "CHANGELOG.md has no link definition for [v$version]"

if command -v shellcheck >/dev/null; then
  shellcheck scripts/*.sh .github/scripts/*.sh
else
  echo "shellcheck not installed; skipping (CI has it)"
fi

echo "all checks passed"
