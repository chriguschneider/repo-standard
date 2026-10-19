"""The command-line entry point answers --version and runs without args."""

from __future__ import annotations

import pytest

from @@DOMAIN@@ import __version__
from @@DOMAIN@@.__main__ import main


def test_version_flag(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
    assert __version__ in capsys.readouterr().out


def test_runs_without_arguments() -> None:
    assert main([]) == 0
