#!/usr/bin/env python3
"""Apply the GitHub side of the standard to an existing GitHub repo.

  labels      standard labels (labels.json) + the type's area labels
  settings    allow auto-merge, squash merge, delete branch on merge
              (+ the default branch, for types with a production branch)
  protection  PR-only default branch with the type's required checks,
              strict off, no force pushes (needs a public repo or a paid
              plan; run it after the first CI run so the checks exist)

Types whose type.json sets PRODUCTION_BRANCH (website: PRs land on `test`,
the owner fast-forwards `main`) also get, in step `protection`: the
production branch created from the default branch if missing, protected
without a PR requirement (the owner pushes a fast-forward) but with the
required checks, linear history, no force push and no deletion, enforced
for admins too; and a ruleset that lets only repository admins update it,
so an agent's write token cannot push there.

Uses the `gh` CLI with the caller's own login. Never touches secrets.

  python3 github-setup.py --repo OWNER/NAME --type ha-integration [--dry-run]
         [--only labels,settings,protection] [--branch master]
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RULESET_NAME = "Production branch: admins only"
# RepositoryRole 5 is the built-in "Repository admin" role.
ADMIN_ROLE = {"actor_id": 5, "actor_type": "RepositoryRole", "bypass_mode": "always"}


def gh(args: list[str], dry: bool, payload: dict | None = None) -> None:
    cmd = ["gh", *args]
    shown = " ".join(cmd) + (f"  <<< {json.dumps(payload)}" if payload else "")
    if dry:
        print("DRY", shown)
        return
    print("RUN", shown)
    subprocess.run(
        cmd + (["--input", "-"] if payload else []),
        input=json.dumps(payload) if payload else None,
        text=True,
        check=True,
        stdout=subprocess.DEVNULL,
    )


def gh_read(args: list[str]) -> str | None:
    """Read-only call; None if it fails (e.g. 404)."""
    out = subprocess.run(["gh", *args], capture_output=True, text=True)
    return out.stdout.strip() if out.returncode == 0 else None


def protect_production(repo: str, default: str, production: str, checks: list[str], dry: bool) -> None:
    if dry:
        print(f"DRY (if {production} is missing) gh api -X POST repos/{repo}/git/refs"
              f"  <<< {{\"ref\": \"refs/heads/{production}\", \"sha\": \"<head of {default}>\"}}")
    elif gh_read(["api", f"repos/{repo}/branches/{production}", "--jq", ".name"]) is None:
        sha = gh_read(["api", f"repos/{repo}/git/ref/heads/{default}", "--jq", ".object.sha"])
        if not sha:
            sys.exit(f"cannot create {production}: branch {default} not found in {repo}")
        gh(["api", "-X", "POST", f"repos/{repo}/git/refs"], dry,
           {"ref": f"refs/heads/{production}", "sha": sha})
    else:
        print(f"OK  {production} exists")

    # No PR requirement: promotion is the owner's fast-forward push. The
    # required checks still apply to that push (the commit has them from its
    # CI run on the default branch), for admins too.
    payload = {
        "required_status_checks": {"strict": False, "contexts": checks},
        "enforce_admins": True,
        "required_pull_request_reviews": None,
        "restrictions": None,
        "required_linear_history": True,
        "allow_force_pushes": False,
        "allow_deletions": False,
    }
    gh(["api", "-X", "PUT", f"repos/{repo}/branches/{production}/protection"], dry, payload)

    # Push restrictions in classic protection are org-only; a ruleset with
    # an admin bypass works on personal repos. Updated in place on re-runs.
    ruleset = {
        "name": RULESET_NAME,
        "target": "branch",
        "enforcement": "active",
        "conditions": {"ref_name": {"include": [f"refs/heads/{production}"], "exclude": []}},
        "rules": [{"type": "update", "parameters": {"update_allows_fetch_and_merge": False}}],
        "bypass_actors": [ADMIN_ROLE],
    }
    existing = None if dry else gh_read(
        ["api", f"repos/{repo}/rulesets", "--jq", f'.[] | select(.name == "{RULESET_NAME}") | .id'])
    if existing:
        gh(["api", "-X", "PUT", f"repos/{repo}/rulesets/{existing.splitlines()[0]}"], dry, ruleset)
    else:
        gh(["api", "-X", "POST", f"repos/{repo}/rulesets"], dry, ruleset)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--type", required=True)
    ap.add_argument("--branch", help="default branch (default: the type's BRANCH, else master)")
    ap.add_argument("--only", default="labels,settings,protection")
    ap.add_argument("--variant", action="append", default=[], help="variants used when rendering")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    spec = json.loads((ROOT / "types" / a.type / "type.json").read_text(encoding="utf-8"))
    placeholders = spec.get("placeholders", {})
    # Variants bring their own required checks and labels (e.g. "Card tests").
    variants = spec.get("variants", {})
    for name in a.variant:
        if name not in variants:
            sys.exit(f"unknown variant {name!r} for {a.type}")
        spec["required_checks"] = [*spec["required_checks"], *variants[name].get("required_checks", [])]
        spec.setdefault("labels", {}).update(variants[name].get("labels", {}))
    branch = a.branch or placeholders.get("BRANCH", "master")
    production = placeholders.get("PRODUCTION_BRANCH")
    steps = set(a.only.split(","))

    if "labels" in steps:
        labels = json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))
        labels.update(spec.get("labels", {}))
        for name, (color, desc) in labels.items():
            gh(["label", "create", name, "-R", a.repo, "--color", color,
                "--description", desc, "--force"], a.dry_run)

    if "settings" in steps:
        # With a production branch, PRs and agents must target the other
        # branch, and "default branch" in every workflow means that one.
        extra = ["--default-branch", branch] if production else []
        gh(["repo", "edit", a.repo, "--enable-auto-merge", "--enable-squash-merge",
            "--delete-branch-on-merge", *extra], a.dry_run)

    if "protection" in steps:
        payload = {
            "required_status_checks": {"strict": False, "contexts": spec["required_checks"]},
            "enforce_admins": False,
            "required_pull_request_reviews": {"required_approving_review_count": 0},
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
        }
        gh(["api", "-X", "PUT", f"repos/{a.repo}/branches/{branch}/protection"],
           a.dry_run, payload)
        if production:
            protect_production(a.repo, branch, production, spec["required_checks"], a.dry_run)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(f"gh failed: {exc}")
