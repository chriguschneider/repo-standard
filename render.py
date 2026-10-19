#!/usr/bin/env python3
"""Render a new repository from this standard.

Copies ``common/``, the chosen ``types/<type>/`` and, for ``--mode
autopilot``, ``modes/autopilot/`` into ``--out``, replacing ``@@KEY@@``
placeholders in file contents and paths.

``@@KEY@@`` is used instead of ``{{key}}`` because GitHub workflow files
are full of ``${{ ... }}`` expressions.

Values, later wins:
  1. built-ins (BRANCH, YEAR, DATE, MODE, STANDARD_URL),
  2. detected identity: OWNER from `gh api user`, AUTHOR from `git config
     user.name`,
  3. your defaults file ($XDG_CONFIG_HOME/repo-standard/defaults.json,
     usually ~/.config/repo-standard/defaults.json), e.g.
     {"OWNER": "octocat", "AUTHOR": "Mona Lisa", "FUNDING_URL": "https://..."},
  4. ``types/<type>/type.json`` -> ``placeholders``,
  5. ``types/<type>/_snippets/<KEY>.md`` (one file per multi-line value),
     then the same for each ``--variant`` (``type.json`` -> ``variants``,
     files in ``types/<type>/variants/<name>/``, overlaid on the type),
  6. ``--set KEY=VALUE`` on the command line.

A placeholder alone on its line is replaced by the value's lines, each with
that line's indentation (works inside YAML block scalars and Markdown); if
the value is empty, the line disappears. That is how optional parts such as
the funding badge drop out.

Stdlib only. Refuses to write into a non-empty directory.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
STANDARD_URL = "https://github.com/chriguschneider/repo-standard"
PLACEHOLDER = re.compile(r"@@([A-Z0-9_]+)@@")
MODES = ("minimal", "opt-in", "autopilot")
# Workflows that only make sense with branch protection + auto-merge.
REVIEW_ONLY = {".github/workflows/claude-review.yml"}
IDENTITY = ("OWNER", "AUTHOR")
CHANGELOG_RULES = """### Changelog entries

Every PR that changes user-visible behavior adds an entry to
`CHANGELOG.md` under `## [Unreleased]` in the right subsection
(Added/Changed/Deprecated/Removed/Fixed/Security, per
[Keep a Changelog](https://keepachangelog.com/en/1.0.0/)).

**Exemption:** a fix for a feature that never appeared in a released
version needs no entry — it has no user-visible before-state.

Write entries for users: would they click *Update* because of this line?
HACS and release pages show the section as is. Internal work (refactors,
CI, tests) goes in a short *Under the hood* list at the end of the section,
or nowhere.

The release commit (`chore(release): vX.Y.Z`) renames `## [Unreleased]`
to `## [vX.Y.Z] — YYYY-MM-DD`; the release workflow extracts that section
verbatim as the GitHub release notes."""


def load_type(name: str) -> dict:
    path = ROOT / "types" / name / "type.json"
    if not path.is_file():
        known = sorted(p.name for p in (ROOT / "types").iterdir() if p.is_dir())
        sys.exit(f"unknown type {name!r}; known: {', '.join(known)}")
    return json.loads(path.read_text(encoding="utf-8"))


def _run(cmd: list[str]) -> str:
    try:
        out = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
    except (OSError, subprocess.TimeoutExpired):
        return ""
    return out.stdout.strip() if out.returncode == 0 else ""


def detected_identity() -> dict[str, str]:
    found = {
        "OWNER": _run(["gh", "api", "user", "--jq", ".login"]),
        "AUTHOR": _run(["git", "config", "user.name"]),
    }
    return {k: v for k, v in found.items() if v}


def user_defaults() -> dict[str, str]:
    base = Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
    path = base / "repo-standard" / "defaults.json"
    if not path.is_file():
        return {}
    return {k.upper(): str(v) for k, v in json.loads(path.read_text(encoding="utf-8")).items()}


def snippets(type_dir: Path) -> dict[str, str]:
    folder = type_dir / "_snippets"
    if not folder.is_dir():
        return {}
    return {p.stem.upper(): p.read_text(encoding="utf-8") for p in sorted(folder.glob("*.md"))}


def funding(values: dict[str, str]) -> None:
    url = values.get("FUNDING_URL", "")
    label = values.get("FUNDING_LABEL", "Sponsor")
    values.setdefault(
        "FUNDING_BADGE",
        f'<a href="{url}"><img alt="{label}" src="https://img.shields.io/badge/'
        f'{label.replace(" ", "%20")}-support-FFDD00.svg" /></a>' if url else "",
    )
    values.setdefault(
        "FUNDING_LINE",
        f"If this is useful to you, [a coffee]({url}) is a nice way to say thanks. "
        "(Claude doesn't drink coffee. More for me.)" if url else "",
    )


def substitute(text: str, values: dict[str, str], missing: set[str]) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        whole = PLACEHOLDER.fullmatch(line.strip())
        if whole and whole.group(1) in values:
            value = values[whole.group(1)].rstrip("\n")
            if not value:
                continue  # optional part not configured: drop the line
            indent = line[: len(line) - len(line.lstrip())]
            ending = "\n" if line.endswith("\n") else ""
            out.append("\n".join(indent + v if v else "" for v in value.split("\n")) + ending)
            continue

        def repl(m: re.Match[str]) -> str:
            key = m.group(1)
            if key not in values:
                missing.add(key)
                return m.group(0)
            return values[key]

        out.append(PLACEHOLDER.sub(repl, line))
    return "".join(out)


def collect(sources: list[Path], skip: set[str]) -> dict[str, Path]:
    """Relative path -> source file; later sources override earlier ones."""
    files: dict[str, Path] = {}
    for src in sources:
        for path in sorted(src.rglob("*")):
            if path.is_dir():
                continue
            rel = path.relative_to(src).as_posix()
            if rel in skip or rel.startswith(("_snippets/", "variants/")):
                continue
            files[rel] = path
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--type", required=True, help="see types/")
    ap.add_argument("--mode", choices=MODES, default="opt-in")
    ap.add_argument("--variant", action="append", default=[], help="see type.json -> variants")
    ap.add_argument("--out", type=Path)
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--list", action="store_true", help="print the placeholders and exit")
    args = ap.parse_args()

    spec = load_type(args.type)
    type_dir = ROOT / "types" / args.type
    today = date.today()
    values: dict[str, str] = {
        "BRANCH": "master",
        "YEAR": str(today.year),
        "DATE": today.isoformat(),
        "MODE": args.mode,
        "STANDARD_URL": STANDARD_URL,
        "FUNDING_URL": "",
        # harden-runner: `audit` until a few agent runs show every endpoint,
        # then `--set EGRESS_POLICY=block` (or edit the workflows).
        "EGRESS_POLICY": "audit",
        # How the reviewer may fix things; types that build artifacts the
        # reviewer cannot rebuild override it.
        # AGENTS.md section on the changelog; types without tag releases
        # (website) replace it.
        "CHANGELOG_RULES": CHANGELOG_RULES,
        "CHANGELOG_GUARD_RULE": (
            "**Changelog** — a user-visible change adds an entry under\n"
            "  `## [Unreleased]`."
        ),
        # Type-specific pitfalls for AGENTS.md (e.g. Home Assistant quirks).
        "TYPE_RULES": "",
        "REVIEW_FIX_RULE": (
            "2. FIX substantive problems yourself on the PR branch (commit +\n"
            "   push; CI re-runs on your push). **At most 3 fix rounds.** Do not\n"
            "   fix pure style nits. Never push to the default branch."
        ),
    }
    values.update(detected_identity())
    values.update(user_defaults())
    values.update(spec.get("placeholders", {}))
    values.update(snippets(type_dir))
    known = spec.get("variants", {})
    for name in args.variant:
        if name not in known:
            sys.exit(f"unknown variant {name!r} for {args.type}; known: {', '.join(known) or 'none'}")
        values.update(known[name].get("placeholders", {}))
        values.update(snippets(type_dir / "variants" / name))
    values["VARIANTS"] = ", ".join(args.variant) or "none"
    for item in args.set:
        key, sep, value = item.partition("=")
        if not sep:
            sys.exit(f"--set expects KEY=VALUE, got {item!r}")
        values[key.strip().upper()] = value.replace("\\n", "\n")
    funding(values)

    # Values may reference other placeholders (e.g. STRUCTURE uses DOMAIN);
    # resolve them a few rounds deep before touching any file.
    for _ in range(5):
        values = {
            k: PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), v)
            for k, v in values.items()
        }

    required = [*IDENTITY, *spec.get("required", [])]
    absent = [k for k in required if not values.get(k)]
    if args.list or absent or not args.out:
        print("required:", ", ".join(required))
        print("set:", ", ".join(f"{k}={values[k]!r}" for k in required if values.get(k)))
        print("optional:", ", ".join(sorted(k for k in values if k not in required)))
        if absent:
            sys.exit(f"missing: {', '.join(absent)} (use --set or the defaults file)")
        if not args.out and not args.list:
            sys.exit("--out is required")
        return

    out: Path = args.out.expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} exists and is not empty; refusing to overwrite")

    sources = [ROOT / "common", type_dir]
    sources += [type_dir / "variants" / name for name in args.variant]
    if args.mode == "autopilot":
        sources.append(ROOT / "modes" / "autopilot")
    # A type (or variant) can drop common files it has no use for, e.g. a
    # website without tag releases has no CHANGELOG.md.
    skip = {"type.json", *spec.get("skip", [])}
    for name in args.variant:
        skip |= set(known[name].get("skip", []))
    if args.mode == "minimal":
        skip |= REVIEW_ONLY

    missing: set[str] = set()
    written = 0
    for rel, src in collect(sources, skip).items():
        target = out / substitute(rel, values, missing)
        target.parent.mkdir(parents=True, exist_ok=True)
        try:
            text = src.read_bytes().decode("utf-8")
        except UnicodeDecodeError:
            shutil.copyfile(src, target)
        else:
            target.write_text(substitute(text, values, missing), encoding="utf-8")
        shutil.copymode(src, target)
        written += 1

    print(f"rendered {written} files into {out} ({args.type}, mode {args.mode}, variants {values['VARIANTS']}, owner {values['OWNER']})")
    if missing:
        print("WARNING: unresolved placeholders:", ", ".join(sorted(missing)))
    todos = [
        f"{p.relative_to(out)}:{n}"
        for p in sorted(out.rglob("*"))
        if p.is_file()
        for n, line in enumerate(_lines(p), 1)
        if "TODO(repo-standard)" in line
    ]
    if todos:
        print("fill in by hand (TODO(repo-standard)):")
        for t in todos:
            print("  ", t)
    for step in spec.get("post_render", []):
        print("next:", step)


def _lines(path: Path) -> list[str]:
    try:
        return path.read_text(encoding="utf-8").splitlines()
    except UnicodeDecodeError:
        return []


if __name__ == "__main__":
    main()
