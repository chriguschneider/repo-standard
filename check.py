#!/usr/bin/env python3
"""Check an existing repo against the standard ("nachziehen").

Read-only. Prints one line per check (OK / MISSING / STALE), security
findings first, and exits 1 if anything is off. Local file checks always
run; GitHub checks run when --github is given (uses `gh` with the caller's
login, only reads secret *names*); vault checks run when --vault is given.

  python3 check.py ~/Projects/<repo> [--github OWNER/NAME] [--vault ~/Projects/athene]
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
AREAS = ("security", "repo", "type", "github", "vault")
results: list[tuple[str, str, str]] = []
# Backticked `*.yml` names in ADRs that are not workflows.
NOT_WORKFLOWS = {"dependabot.yml", "services.yaml", "quality_scale.yaml", "docker-compose.yml"}


def report(ok: bool | None, area: str, what: str, stale: bool = False, todo: bool = False) -> None:
    # TODO = expected in a fresh render (a placeholder still to replace);
    # shown, but not a failure.
    status = "OK" if ok else ("TODO" if todo else ("STALE" if stale else "MISSING"))
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
    if any(repo.glob("astro.config.*")) and (repo / "public" / "_headers").is_file():
        return "website"
    if (repo / "Dockerfile").is_file() and "@sveltejs/kit" in text(repo / "package.json"):
        return "webapp"
    if (repo / "pyproject.toml").is_file() and (repo / "src").is_dir():
        return "python"
    if (repo / "VERSION").is_file() and (repo / "scripts" / "check.sh").is_file():
        return "generic"
    return None


def load_spec(repo_type: str | None) -> dict:
    if not repo_type:
        return {}
    return json.loads(text(ROOT / "types" / repo_type / "type.json"))


def detect_variants(repo: Path, repo_type: str | None) -> list[str]:
    if repo_type == "ha-integration" and any(repo.glob("custom_components/*/frontend")):
        return ["with-card"]
    return []


def required_checks(spec: dict, variants: list[str]) -> list[str]:
    checks = list(spec.get("required_checks", []))
    for name in variants:
        checks += spec.get("variants", {}).get(name, {}).get("required_checks", [])
    return checks


def ci_job_names(repo: Path) -> set[str]:
    body = text(repo / ".github/workflows/ci.yml")
    jobs = body.split("\njobs:", 1)[-1] if "\njobs:" in body else ""
    return set(re.findall(r"^    name:\s*[\"']?(.+?)[\"']?\s*$", jobs, re.M))


def security_checks(repo: Path) -> None:
    wf = repo / ".github" / "workflows"
    unpinned = sorted({
        f"{p.name}: {m.group(1)}"
        for p in wf.glob("*.y*ml")
        for m in re.finditer(r"^\s*-?\s*uses:\s*([^\s#]+)", text(p), re.M)
        if not m.group(1).startswith("./") and not re.search(r"@[0-9a-f]{40}$", m.group(1))
    })
    report(not unpinned, "security", "actions pinned by commit SHA" + (f" ({len(unpinned)} not: {', '.join(unpinned[:4])}{' …' if len(unpinned) > 4 else ''})" if unpinned else ""), stale=bool(unpinned))
    report((repo / ".claude/ci-settings.json").is_file(), "security", "agent CI settings (.claude/ci-settings.json)")
    report((repo / ".claude/hooks/protect-paths.py").is_file(), "security", "path guard hook (.claude/hooks/protect-paths.py)")

    for path in sorted(wf.glob("claude-*.yml")):
        body = text(path)
        if "actions/checkout" in body:
            report("persist-credentials: false" in body, "security", f"{path.name}: persist-credentials false")
        if "claude-code-action" in body:
            skip = "--dangerously-skip-permissions" in body
            report(not skip, "security", f"{path.name}: tool allowlist instead of --dangerously-skip-permissions", stale=skip)
            report("harden-runner" in body, "security", f"{path.name}: harden-runner (egress)")
    labeled = text(wf / "claude-labeled.yml")
    if labeled:
        report("author_association" in labeled, "security", "claude-labeled.yml only works trusted issue text")
    review = text(wf / "claude-review.yml")
    if review:
        report("pytest" not in review and "npm test" not in review, "security", "reviewer does not run PR-controlled checks", stale=True)
        report("Hold sensitive paths" in review, "security", "reviewer holds sensitive paths for a human")


def allowlist(body: str) -> list[str] | None:
    m = re.search(r'--allowedTools "([^"]*)"', body)
    return [t for t in m.group(1).split(",") if t] if m else None


def agent_guidance_checks(repo: Path) -> None:
    """The agent workflows carry the standard's allowlist base and refusal
    guidance. A repo set up before these were added keeps an allowlist that
    refuses grep/head/tail and chained commands, and its agent gives up on the
    first refusal (chriguschneider/chriguschneider#28)."""
    wf = repo / ".github" / "workflows"
    tpl = text(ROOT / "common/.github/workflows/claude-labeled.yml")
    base = [t for t in allowlist(tpl) or [] if "@@" not in t]
    for name in ("claude-labeled.yml", "claude-mention.yml"):
        body = text(wf / name)
        have = allowlist(body)
        if have is None:
            continue  # no workflow, or no allowlist (already a security finding)
        missing = [t for t in base if t not in have]
        report(not missing, "repo", f"{name}: allowlist has the standard base" + (f" (missing {len(missing)}: {', '.join(missing[:4])}{' …' if len(missing) > 4 else ''})" if missing else ""), stale=bool(missing))
    labeled = text(wf / "claude-labeled.yml")
    if allowlist(labeled) is not None:
        report("checks every command of a chain" in labeled, "repo", "claude-labeled.yml: prompt explains refused calls (chain rule)", stale=True)
    mention = text(wf / "claude-mention.yml")
    if allowlist(mention) is not None:
        report("--append-system-prompt" in mention, "repo", "claude-mention.yml: system prompt explains refused calls", stale=True)
        report("Report refused tool calls" in mention, "repo", "claude-mention.yml: reports refused tool calls", stale=True)


def repo_checks(repo: Path, repo_type: str | None, spec: dict) -> None:
    wf = repo / ".github" / "workflows"
    skipped = set(spec.get("skip", []))
    # Types with a promote flow (website) have no tag release.
    has_release = not repo_type or (ROOT / "types" / repo_type / ".github/workflows/release.yml").is_file()
    files = {
        "AGENTS.md with Shared Skeleton": ("AGENTS.md", "Shared Skeleton"),
        "CLAUDE.md imports AGENTS.md": ("CLAUDE.md", "@AGENTS.md"),
        ".gitignore keeps CLAUDE.local.md local": (".gitignore", "CLAUDE.local.md"),
        "ADR index": ("docs/adr/README.md", "When to write one"),
        "docs/agent-automation.md with sizing rules": ("docs/agent-automation.md", "Sizing an issue"),
        "commit-guardian skill": (".claude/skills/commit-guardian/SKILL.md", "name: commit-guardian"),
        "documentation-guardian skill": (".claude/skills/documentation-guardian/SKILL.md", "name: documentation-guardian"),
        "CI workflow named CI": (".github/workflows/ci.yml", "name: CI"),
        "CI also runs weekly": (".github/workflows/ci.yml", "schedule:"),
        "CI watch on the default branch": (".github/workflows/ci-watch.yml", "CI is red on"),
        "CodeQL": (".github/workflows/codeql.yml", "codeql-action"),
        "Dependabot with cooldown": (".github/dependabot.yml", "cooldown:"),
        "label workflow (agent:go)": (".github/workflows/claude-labeled.yml", "agent:go"),
        "mention workflow with author gate": (".github/workflows/claude-mention.yml", "author_association"),
    }
    if "CHANGELOG.md" not in skipped:
        files["CHANGELOG.md with [Unreleased]"] = ("CHANGELOG.md", "## [Unreleased]")
    if has_release:
        files["release workflow (tag push)"] = (".github/workflows/release.yml", "tags:")
        files["release requires green CI on the tag"] = (".github/workflows/release.yml", "--status success")
    for what, (rel, needle) in files.items():
        report(needle in text(repo / rel), "repo", what)

    ignore = text(repo / ".gitignore")
    if re.search(r"^/?CLAUDE\.md$", ignore, re.M):
        report(False, "repo", ".gitignore still ignores CLAUDE.md (track a thin one with @AGENTS.md)", stale=True)
    auto = text(repo / "docs/agent-automation.md")
    if "lacks the\n  `workflows` permission" in auto or "lacks the `workflows` permission" in auto:
        report(False, "repo", "docs/agent-automation.md claims the token lacks the workflows permission", stale=True)

    # Mode `minimal` (no branch protection) deliberately has no reviewer.
    mode = re.search(r"runs in mode \*\*`([\w-]+)`", auto)
    if not (mode and mode.group(1) == "minimal"):
        body = text(wf / "claude-review.yml")
        report("deadlocking" in body, "repo", "reviewer with CI watch")
        on_opened = bool(re.search(r"types:\s*\[[^\]]*\bopened\b", body.split("\njobs:", 1)[0]))
        report("ready_for_review" in body and not on_opened, "repo", "reviewer starts when the agent is done, not when the draft opens", stale=on_opened)

    pick = text(repo / ".github/scripts/pick-model.sh")
    if not pick:
        report(False, "repo", "pick-model.sh")
    else:
        pinned = re.findall(r'model="(claude-[^"]+)"', pick)
        report(not pinned, "repo", "pick-model.sh uses aliases" + (f" (pinned: {', '.join(sorted(set(pinned)))})" if pinned else ""), stale=bool(pinned))
    if (wf / "claude-labeled.yml").is_file():
        report((repo / ".github/scripts/after-agent-run.sh").is_file(), "repo", "after-agent-run.sh (keeps work, hands over to the reviewer)")
        report("after-agent-run.sh" in text(wf / "claude-labeled.yml"), "repo", "claude-labeled.yml runs after-agent-run.sh")
    for path in sorted(wf.glob("claude-*.yml")):
        pinned = re.findall(r"--model (claude-[\w.-]+)", text(path))
        if pinned:
            report(False, "repo", f"{path.name}: pinned model {pinned[0]}", stale=True)

    # Workflows the ADRs rely on must exist (an agent cannot write them, so
    # they are the half of a change that gets lost).
    named = {
        m for adr in (repo / "docs/adr").glob("*.md")
        for m in re.findall(r"`(?:\.github/workflows/)?([\w.-]+\.ya?ml)`", text(adr))
        if m not in NOT_WORKFLOWS
    }
    absent = sorted(n for n in named if not (wf / n).is_file() and n.startswith(("ci", "release", "smoke", "codeql", "claude", "sonar", "validate", "build", "badges", "deploy", "ci-watch", "update")))
    if named:
        report(not absent, "repo", "workflows named in ADRs exist" + (f" (missing: {', '.join(absent)})" if absent else ""))


def type_checks(repo: Path, repo_type: str | None, spec: dict, variants: list[str]) -> None:
    if not repo_type:
        return
    need = required_checks(spec, variants)
    have = ci_job_names(repo)
    # Older card repos run HACS validation in a separate validate.yml.
    elsewhere = {"HACS validation"} if (repo / ".github/workflows/validate.yml").is_file() else set()
    missing = [c for c in need if c not in have and c not in elsewhere]
    report(not missing, "type", "ci.yml job names match the required checks" + (f" (missing: {', '.join(missing)})" if missing else ""))

    if repo_type == "ha-integration":
        comp = next(iter(sorted(repo.glob("custom_components/*/manifest.json"))), None)
        domain = comp.parent if comp else None
        report(bool(list((repo / "tests").glob("test_*.py"))), "type", "tests/ with pytest tests")
        report(bool(re.search(r'"zip_release"\s*:\s*true', text(repo / "hacs.json"))), "type", "hacs.json zip_release")
        if domain:
            report(bool(re.search(r'^VERSION\s*=', text(domain / "const.py"), re.M)), "type", "const.py VERSION")
            report((domain / "diagnostics.py").is_file(), "type", "diagnostics.py")
            placeholder = ROOT / "types/ha-integration/custom_components/@@DOMAIN@@/brand/icon.png"
            icon = domain / "brand" / "icon.png"
            if icon.is_file() and placeholder.is_file():
                same = hashlib.sha256(icon.read_bytes()).digest() == hashlib.sha256(placeholder.read_bytes()).digest()
                report(not same, "type", "brand icon replaced (still the scaffold placeholder)", todo=True)
            else:
                report(icon.is_file(), "type", "brand/icon.png in the integration")
    labeled = text(repo / ".github/workflows/claude-labeled.yml")
    if labeled and repo_type in ("ha-integration", "python"):
        report("setup-python" in labeled, "type", "agent job sets up Python (else it cannot run the checks)")
    if labeled and repo_type in ("lovelace-card", "website", "webapp"):
        report("setup-node" in labeled, "type", "agent job sets up Node (else it cannot run the checks)")
    if repo_type == "lovelace-card":
        report(bool(list((repo / "dist").glob("*.js"))), "type", "committed dist/ bundle (run npm run build)", todo=True)
        report(bool(list((repo / "tests").glob("*.test.*"))), "type", "tests/ with vitest tests")
    if repo_type == "python":
        report(bool(list((repo / "tests").glob("test_*.py"))), "type", "tests/ with pytest tests")
    elif repo_type == "website":
        report("astro check" in text(repo / "package.json"), "type", "build runs astro check")
    elif repo_type == "webapp":
        report(bool(list((repo / "src").rglob("*.test.ts"))), "type", "src/ with vitest tests")
        report(bool(list((repo / "tests").glob("*.spec.ts"))), "type", "tests/ with Playwright specs")
        report("HEALTHCHECK" in text(repo / "Dockerfile"), "type", "Dockerfile with HEALTHCHECK")
        report(bool(list((repo / "drizzle").glob("*.sql"))), "type", "drizzle/ with committed migrations")
        report("migrate(" in text(repo / "src/hooks.server.ts"), "type", "migrations run on startup (hooks.server.ts)")


def gh_json(args: list[str]):
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    if out.returncode != 0:
        return None
    try:
        return json.loads(out.stdout)
    except json.JSONDecodeError:
        return None


def github_checks(repo_id: str, spec: dict, variants: list[str]) -> None:
    info = gh_json(["api", f"repos/{repo_id}"]) or {}
    branch = info.get("default_branch", "master")
    placeholders = spec.get("placeholders", {})
    if placeholders.get("BRANCH"):
        report(branch == placeholders["BRANCH"], "github", f"default branch is {placeholders['BRANCH']}")
    report(info.get("allow_auto_merge") is True, "github", "auto-merge allowed")
    report(info.get("delete_branch_on_merge") is True, "github", "delete branch on merge")
    # after-agent-run.sh opens the leftover PR with GITHUB_TOKEN; GitHub refuses
    # that unless Actions may create pull requests (github-setup.py sets it).
    perms = gh_json(["api", f"repos/{repo_id}/actions/permissions/workflow"]) or {}
    report(perms.get("default_workflow_permissions") == "read" and perms.get("can_approve_pull_request_reviews") is True,
           "github", "Actions may create pull requests, token read-only by default")

    wanted = set(json.loads(text(ROOT / "labels.json"))) | set(spec.get("labels", {}))
    have = {lbl["name"] for lbl in gh_json(["label", "list", "-R", repo_id, "--limit", "200", "--json", "name"]) or []}
    missing = sorted(wanted - have)
    report(not missing, "github", "labels" + (f" (missing: {', '.join(missing)})" if missing else ""))

    prot = gh_json(["api", f"repos/{repo_id}/branches/{branch}/protection"])
    report(prot is not None, "github", f"branch protection on {branch}")
    if prot and spec:
        req = set(prot.get("required_status_checks", {}).get("contexts", []))
        need = set(required_checks(spec, variants))
        report(need <= req, "github", "required checks" + (f" (missing: {', '.join(sorted(need - req))})" if need - req else ""))
    production = placeholders.get("PRODUCTION_BRANCH")
    if production:
        report(gh_json(["api", f"repos/{repo_id}/branches/{production}/protection"]) is not None, "github", f"branch protection on {production}")

    runs = gh_json(["run", "list", "-R", repo_id, "--workflow", "ci.yml", "--branch", branch, "--limit", "1", "--json", "conclusion,status"]) or []
    if runs:
        last = runs[0].get("conclusion") or runs[0].get("status")
        report(last in ("success", "in_progress", "queued"), "github", f"last CI run on {branch}: {last}")

    secrets = {s["name"] for s in gh_json(["secret", "list", "-R", repo_id, "--json", "name"]) or []}
    report("CLAUDE_CODE_OAUTH_TOKEN" in secrets, "github", "secret CLAUDE_CODE_OAUTH_TOKEN (name only)")


def vault_checks(vault: Path, name: str, spec: dict) -> None:
    effort = vault / "Efforts" / name
    report((effort / f"MOC-{name}.md").is_file(), "vault", f"Efforts/{name}/MOC-{name}.md")
    report((effort / "CLAUDE.md").is_file(), "vault", f"Efforts/{name}/CLAUDE.md")
    links = ["README.md", "AGENTS.md", "docs"]
    if "CHANGELOG.md" not in spec.get("skip", []):
        links.insert(2, "CHANGELOG.md")
    for rel in links:
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
    spec = load_spec(repo_type)
    variants = detect_variants(repo, repo_type)
    print(f"{repo.name}: type {repo_type or 'unknown'}" + (f", variants {', '.join(variants)}" if variants else ""))

    security_checks(repo)
    repo_checks(repo, repo_type, spec)
    agent_guidance_checks(repo)
    type_checks(repo, repo_type, spec, variants)
    if a.github:
        github_checks(a.github, spec, variants)
    if a.vault:
        vault_checks(a.vault.expanduser().resolve(), repo.name, spec)

    for status, area, what in sorted(results, key=lambda r: AREAS.index(r[1])):
        print(f"{status:8} {area:8} {what}")
    bad = [r for r in results if r[0] not in ("OK", "TODO")]
    todo = sum(r[0] == "TODO" for r in results)
    print(f"\n{len(results) - len(bad) - todo}/{len(results)} OK" + (f", {todo} TODO" if todo else ""))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
