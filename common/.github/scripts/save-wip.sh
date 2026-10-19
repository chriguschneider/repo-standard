#!/usr/bin/env bash
# Runs after every agent implementation step, success or not. If the agent
# left work on a `claude/*` branch that is not on GitHub yet -- uncommitted
# files or unpushed commits, typically because the run hit the turn or time
# limit -- commit and push it and make sure a draft PR exists, labelled
# `agent:needs-continuation`. A run that dies at the limit used to leave
# nothing behind.
#
# Pushes with the workflow's GITHUB_TOKEN on purpose: that push does not
# trigger CI or the reviewer, so unfinished work is never auto-merged.
#
# Usage: save-wip.sh <issue-number> <step-outcome>. Needs GH_TOKEN,
# GITHUB_REPOSITORY and DEFAULT_BRANCH in the environment.
set -euo pipefail

issue="${1:?usage: save-wip.sh <issue> <outcome>}"
outcome="${2:-unknown}"

branch="$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo HEAD)"
case "$branch" in
  claude/*) ;;
  *) echo "not on an agent branch ($branch); nothing to save"; exit 0 ;;
esac

git config user.name "claude[bot]"
git config user.email "209825114+claude[bot]@users.noreply.github.com"

if [ -n "$(git status --porcelain)" ]; then
  git add -A
  git commit -q -m "wip: unfinished agent run for #$issue" \
    -m "The run ended ($outcome) before the agent committed this. Saved by save-wip.sh."
  echo "committed leftover changes"
fi

default="${DEFAULT_BRANCH:-master}"
if [ "$(git rev-list --count "origin/$default..HEAD" 2>/dev/null || echo 0)" = "0" ]; then
  echo "branch has no commits beyond $default; nothing to save"
  exit 0
fi

remote="https://x-access-token:${GH_TOKEN}@github.com/${GITHUB_REPOSITORY}.git"
if ! git push -q "$remote" "HEAD:refs/heads/$branch"; then
  echo "::warning::could not push $branch (remote moved on?); leaving it to a human"
  exit 0
fi

pr="$(gh pr list --head "$branch" --state open --json number --jq '.[0].number // empty')"
if [ -z "$pr" ]; then
  # shellcheck disable=SC2016 # the backticks are Markdown, not a command
  gh pr create --draft --head "$branch" \
    --title "WIP: #$issue (agent run did not finish)" \
    --body "$(printf 'The agent run for #%s ended (%s) before it opened a PR. This draft holds what it had.\n\nContinue with a comment `@claude continue with #%s`, or take it over by hand.\n\nRefs #%s' "$issue" "$outcome" "$issue" "$issue")"
  pr="$(gh pr list --head "$branch" --state open --json number --jq '.[0].number')"
fi

if [ "$outcome" != "success" ]; then
  gh pr edit "$pr" --add-label agent:needs-continuation || true
  gh pr comment "$pr" --body "Agent run ended with **$outcome**; unfinished work was saved here. Run: $GITHUB_SERVER_URL/$GITHUB_REPOSITORY/actions/runs/$GITHUB_RUN_ID" || true
fi
echo "saved to PR #$pr"
