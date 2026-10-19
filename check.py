#!/usr/bin/env python3
"""Check an existing repo against the standard ("nachziehen").

Read-only. Prints one line per check (OK / MISSING / STALE) and exits 1 if
anything is off. Local file checks always run; GitHub checks run when
--github is given (uses `gh` with the caller's login, only reads secret
*names*); vault checks run when --vault is given.

  python3 check.py ~/Projects/<repo> [--github OWNER/NAME] [--vault ~/Projects/athene]
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
results: list[tuple[str, str, str]] = []


def report(ok: bool | None, area: str, what: str, stale: bool = False) -> None:
    status = "OK" if ok else ("STALE" if stale else "MISSING")
    results.append((status, area, what))


def text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError, UnicodeDecodeError):
        return ""


def detect_type(repo: Path) -> str | None:
    if (repo / "hacs.json").is_file() and (repo / "custom_components").is_dir():
        return "ha-integration"
    if (repo / "hacs.json").is_file() and (repo / "package.json").is_file():
        return "lovelace-card"
    if (repo / "pyproject.toml").is_file() and (repo / "src").is_dir():
        return "python"
    if (repo / "VERSION").is_file() and (repo / "scripts" / "check.sh").is_file():
        return "generic"
    return None


def local_checks(repo: Path) -> None:
    wf = repo / ".github" / "workflows"
    files = {
        "AGENTS.md with Shared Skeleton": ("AGENTS.md", "Shared Skeleton"),
        "CHANGELOG.md with [Unreleased]": ("CHANGELOG.md", "## [Unreleased]"),
        "ADR index": ("docs/adr/README.md", "When to write one"),
        "docs/agent-automation.md": ("docs/agent-automation.md", "agent:go"),
        "commit-guardian skill": (".claude/skills/commit-guardian/SKILL.md", "name: commit-guardian"),
        "documentation-guardian skill": (".claude/skills/documentation-guardian/SKILL.md", "name: documentation-guardian"),
        "CI workflow named CI": (".github/workflows/ci.yml", "name: CI"),
        "release workflow (tag push)": (".github/workflows/release.yml", "tags:"),
        "CodeQL": (".github/workflows/codeql.yml", "codeql-action"),
        "Dependabot": (".github/dependabot.yml", "package-ecosystem"),
        "label workflow (agent:go)": (".github/workflows/claude-labeled.yml", "agent:go"),
        "mention workflow with author gate": (".github/workflows/claude-mention.yml", "author_association"),
        ".gitignore keeps CLAUDE.md local": (".gitignore", "CLAUDE.md"),
    }
    for what, (rel, needle) in files.items():
        report(needle in text(repo / rel), "repo", what)

    # Mode `minimal` (no branch protection) deliberately has no reviewer.
    mode = re.search(r"runs in mode \*\*`([\w-]+)`", text(repo / "docs/agent-automation.md"))
    if not (mode and mode.group(1) == "minimal"):
        body = text(wf / "claude-review.yml")
        report("deadlocking" in body, "repo", "reviewer with CI watch")

    pick = text(repo / ".github/scripts/pick-model.sh")
    if not pick:
        report(False, "repo", "pick-model.sh")
    else:
        pinned = re.findall(r'model="(claude-[^"]+)"', pick)
        report(not pinned, "repo", "pick-model.sh uses aliases" + (f" (pinned: {', '.join(sorted(set(pinned)))})" if pinned else ""), stale=bool(pinned))

    report((repo / ".claude/ci-settings.json").is_file(), "repo", "agent CI settings (.claude/ci-settings.json)")
    report((repo / ".claude/hooks/protect-paths.py").is_file(), "repo", "path guard hook (.claude/hooks/protect-paths.py)")
    if (wf / "claude-labeled.yml").is_file():
        report((repo / ".github/scripts/save-wip.sh").is_file(), "repo", "save-wip.sh (keeps work when a run hits the limit)")
        report("save-wip.sh" in text(wf / "claude-labeled.yml"), "repo", "claude-labeled.yml saves unfinished work")
        report("author_association" in text(wf / "claude-labeled.yml"), "repo", "claude-labeled.yml only works trusted issue text")
    if (wf / "claude-review.yml").is_file():
        body = text(wf / "claude-review.yml")
        report("Hold sensitive paths" in body, "repo", "reviewer holds sensitive paths for a human")
        report("pytest" not in body and "npm test" not in body, "repo", "reviewer does not run PR-controlled checks", stale=True)

    unpinned = sorted({
        f"{p.name}: {m.group(1)}"
        for p in wf.glob("*.y*ml")
        for m in re.finditer(r"^\s*-?\s*uses:\s*([^\s#]+)", text(p), re.M)
        if not m.group(1).startswith("./") and not re.search(r"@[0-9a-f]{40}$", m.group(1))
    })
    report(not unpinned, "repo", "actions pinned by commit SHA" + (f" ({len(unpinned)} not: {', '.join(unpinned[:4])}{' …' if len(unpinned) > 4 else ''})" if unpinned else ""), stale=bool(unpinned))

    for path in sorted(wf.glob("claude-*.yml")):
        body = text(path)
        if "actions/checkout" in body:
            report("persist-credentials: false" in body, "repo", f"{path.name}: persist-credentials false")
        if "claude-code-action" in body:
            report("harden-runner" in body, "repo", f"{path.name}: harden-runner (egress)")
            report("--dangerously-skip-permissions" not in body, "repo", f"{path.name}: tool allowlist instead of --dangerously-skip-permissions", stale="--dangerously-skip-permissions" in body)
        pinned = re.findall(r"--model (claude-[\w.-]+)", body)
        if pinned:
            report(False, "repo", f"{path.name}: pinned model {pinned[0]}", stale=True)


def gh_json(args: list[str]):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def github_checks(repo_id: str, repo_type: str | None) -> None:
    info = gh_json(["api", f"repos/{repo_id}"]) or {}
    branch = info.get("default_branch", "master")
    report(info.get("allow_auto_merge") is True, "github", "auto-merge allowed")
    report(info.get("delete_branch_on_merge") is True, "github", "delete branch on merge")

    wanted = set(json.loads(text(ROOT / "labels.json")))
    if repo_type:
        spec = json.loads(text(ROOT / "types" / repo_type / "type.json"))
        wanted |= set(spec.get("labels", {}))
    have = {lbl["name"] for lbl in gh_json(["label", "list", "-R", repo_id, "--limit", "200", "--json", "name"]) or []}
    missing = sorted(wanted - have)
    report(not missing, "github", "labels" + (f" (missing: {', '.join(missing)})" if missing else ""))

    prot = gh_json(["api", f"repos/{repo_id}/branches/{branch}/protection"])
    report(prot is not None, "github", f"branch protection on {branch}")
    if prot and repo_type:
        req = set(prot.get("required_status_checks", {}).get("contexts", []))
        need = set(json.loads(text(ROOT / "types" / repo_type / "type.json"))["required_checks"])
        report(need <= req, "github", "required checks" + (f" (missing: {', '.join(sorted(need - req))})" if need - req else ""))

    secrets = {s["name"] for s in gh_json(["secret", "list", "-R", repo_id, "--json", "name"]) or []}
    report("CLAUDE_CODE_OAUTH_TOKEN" in secrets, "github", "secret CLAUDE_CODE_OAUTH_TOKEN (name only)")


def vault_checks(vault: Path, name: str) -> None:
    effort = vault / "Efforts" / name
    report((effort / f"MOC-{name}.md").is_file(), "vault", f"Efforts/{name}/MOC-{name}.md")
    report((effort / "CLAUDE.md").is_file(), "vault", f"Efforts/{name}/CLAUDE.md")
    for rel in ("README.md", "AGENTS.md", "CHANGELOG.md", "docs"):
        link = effort / "repo" / rel
        report(link.is_symlink() and link.exists(), "vault", f"Efforts/{name}/repo/{rel} symlink")
    moc = text(vault / "Atlas" / "Maps" / "MOC-Vault.md")
    report(f"MOC-{name}" in moc, "vault", "listed in MOC-Vault")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("repo", type=Path)
    ap.add_argument("--github", metavar="OWNER/NAME")
    ap.add_argument("--vault", type=Path)
    a = ap.parse_args()
    repo = a.repo.expanduser().resolve()
    repo_type = detect_type(repo)
    print(f"{repo.name}: type {repo_type or 'unknown'}")

    local_checks(repo)
    if a.github:
        github_checks(a.github, repo_type)
    if a.vault:
        vault_checks(a.vault.expanduser().resolve(), repo.name)

    for status, area, what in results:
        print(f"{status:8} {area:7} {what}")
    bad = [r for r in results if r[0] != "OK"]
    print(f"\n{len(results) - len(bad)}/{len(results)} OK")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
