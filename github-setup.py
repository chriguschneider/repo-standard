#!/usr/bin/env python3
"""Apply the GitHub side of the standard to an existing GitHub repo.

  labels      standard labels (labels.json) + the type's area labels
  settings    allow auto-merge, squash merge, delete branch on merge
  protection  PR-only default branch with the type's required checks,
              strict off, no force pushes (needs a public repo or a paid
              plan; run it after the first CI run so the checks exist)

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


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--repo", required=True)
    ap.add_argument("--type", required=True)
    ap.add_argument("--branch", default="master")
    ap.add_argument("--only", default="labels,settings,protection")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()
    spec = json.loads((ROOT / "types" / a.type / "type.json").read_text(encoding="utf-8"))
    steps = set(a.only.split(","))

    if "labels" in steps:
        labels = json.loads((ROOT / "labels.json").read_text(encoding="utf-8"))
        labels.update(spec.get("labels", {}))
        for name, (color, desc) in labels.items():
            gh(["label", "create", name, "-R", a.repo, "--color", color,
                "--description", desc, "--force"], a.dry_run)

    if "settings" in steps:
        gh(["repo", "edit", a.repo, "--enable-auto-merge", "--enable-squash-merge",
            "--delete-branch-on-merge"], a.dry_run)

    if "protection" in steps:
        payload = {
            "required_status_checks": {"strict": False, "contexts": spec["required_checks"]},
            "enforce_admins": False,
            "required_pull_request_reviews": {"required_approving_review_count": 0},
            "restrictions": None,
            "allow_force_pushes": False,
            "allow_deletions": False,
        }
        gh(["api", "-X", "PUT", f"repos/{a.repo}/branches/{a.branch}/protection"],
           a.dry_run, payload)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as exc:
        sys.exit(f"gh failed: {exc}")
