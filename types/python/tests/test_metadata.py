"""Pure metadata guards: version sync and changelog. Stdlib only."""

from __future__ import annotations

import re
import tomllib
from pathlib import Path

import @@DOMAIN@@

ROOT = Path(__file__).resolve().parent.parent
CHANGELOG = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")


def _project_version() -> str:
    with (ROOT / "pyproject.toml").open("rb") as fh:
        return tomllib.load(fh)["project"]["version"]


def test_versions_are_in_sync() -> None:
    assert @@DOMAIN@@.__version__ == _project_version()


def test_changelog_has_unreleased_section() -> None:
    assert re.search(r"^## \[Unreleased\]", CHANGELOG, re.MULTILINE)


def test_changelog_has_section_and_link_for_current_version() -> None:
    version = _project_version()
    assert re.search(rf"^## \[v{re.escape(version)}\]", CHANGELOG, re.MULTILINE), (
        f"CHANGELOG.md has no '## [v{version}]' section"
    )
    assert f"[v{version}]:" in CHANGELOG, f"no link definition for [v{version}]"
