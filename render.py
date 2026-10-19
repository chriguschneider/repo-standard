#!/usr/bin/env python3
"""Render a new repository from this standard.

Copies ``common/``, the chosen ``types/<type>/`` (minus ``type.json``) and,
for ``--mode autopilot``, ``modes/autopilot/`` into ``--out``, replacing
``@@KEY@@`` placeholders in file contents and paths.

``@@KEY@@`` is used instead of ``{{key}}`` because GitHub workflow files
are full of ``${{ ... }}`` expressions.

Values come from three places, later wins:
  1. built-ins (OWNER, BRANCH, YEAR, DATE),
  2. ``types/<type>/type.json`` -> ``placeholders``,
  3. ``--set KEY=VALUE`` on the command line.

A multi-line value replaces a placeholder that sits alone on its line with
one line per value line, each carrying that line's indentation, so values
can be injected into YAML block scalars and Markdown lists alike.

Stdlib only. Refuses to write into a non-empty directory.
"""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PLACEHOLDER = re.compile(r"@@([A-Z0-9_]+)@@")
MODES = ("minimal", "opt-in", "autopilot")
# Workflows that only make sense with branch protection + auto-merge.
REVIEW_ONLY = {".github/workflows/claude-review.yml"}


def load_type(name: str) -> dict:
    path = ROOT / "types" / name / "type.json"
    if not path.is_file():
        known = sorted(p.name for p in (ROOT / "types").iterdir() if p.is_dir())
        sys.exit(f"unknown type {name!r}; known: {', '.join(known)}")
    return json.loads(path.read_text(encoding="utf-8"))


def substitute(text: str, values: dict[str, str], missing: set[str]) -> str:
    out: list[str] = []
    for line in text.splitlines(keepends=True):
        stripped = line.strip()
        whole = PLACEHOLDER.fullmatch(stripped)
        if whole and "\n" in values.get(whole.group(1), ""):
            indent = line[: len(line) - len(line.lstrip())]
            ending = "\n" if line.endswith("\n") else ""
            body = values[whole.group(1)].rstrip("\n").split("\n")
            out.append("\n".join(indent + v if v else "" for v in body) + ending)
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
            if rel in skip:
                continue
            files[rel] = path
    return files


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--type", required=True, help="e.g. ha-integration, lovelace-card")
    ap.add_argument("--mode", choices=MODES, default="opt-in")
    ap.add_argument("--out", required=True, type=Path)
    ap.add_argument("--set", action="append", default=[], metavar="KEY=VALUE")
    ap.add_argument("--list", action="store_true", help="print the placeholders and exit")
    args = ap.parse_args()

    spec = load_type(args.type)
    today = date.today()
    values: dict[str, str] = {
        "OWNER": "chriguschneider",
        "BRANCH": "master",
        "YEAR": str(today.year),
        "DATE": today.isoformat(),
        "MODE": args.mode,
    }
    values.update(spec.get("placeholders", {}))
    for item in args.set:
        key, sep, value = item.partition("=")
        if not sep:
            sys.exit(f"--set expects KEY=VALUE, got {item!r}")
        values[key.strip().upper()] = value.replace("\\n", "\n")

    # Values may reference other placeholders (e.g. STRUCTURE uses DOMAIN);
    # resolve them a few rounds deep before touching any file.
    for _ in range(5):
        values = {
            k: PLACEHOLDER.sub(lambda m: values.get(m.group(1), m.group(0)), v)
            for k, v in values.items()
        }

    required = spec.get("required", [])
    absent = [k for k in required if not values.get(k)]
    if args.list or absent:
        print("required (--set):", ", ".join(required))
        print("defaults:", ", ".join(sorted(k for k in values if k not in required)))
        if absent:
            sys.exit(f"missing: {', '.join(absent)}")
        return

    out: Path = args.out.expanduser().resolve()
    if out.exists() and any(out.iterdir()):
        sys.exit(f"{out} exists and is not empty; refusing to overwrite")

    sources = [ROOT / "common", ROOT / "types" / args.type]
    if args.mode == "autopilot":
        sources.append(ROOT / "modes" / "autopilot")
    skip = {"type.json"}
    if args.mode == "minimal":
        skip |= REVIEW_ONLY

    missing: set[str] = set()
    written = 0
    for rel, src in collect(sources, skip).items():
        target = out / substitute(rel, values, missing)
        target.parent.mkdir(parents=True, exist_ok=True)
        data = src.read_bytes()
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            shutil.copyfile(src, target)
        else:
            target.write_text(substitute(text, values, missing), encoding="utf-8")
        shutil.copymode(src, target)
        written += 1

    print(f"rendered {written} files into {out} ({args.type}, mode {args.mode})")
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
