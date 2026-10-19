"""The smoke-test script's own logic (no network)."""

from __future__ import annotations

from tests.tools import smoke_test


def test_no_checks_passes_with_a_notice(capsys) -> None:
    assert smoke_test.run([]) == 0
    assert "No smoke checks defined yet" in capsys.readouterr().out


def test_empty_data_counts_as_pass() -> None:
    def check_empty() -> list:
        return []

    assert smoke_test.run([check_empty]) == 0


def test_a_raising_check_fails_the_run(capsys) -> None:
    def check_ok() -> list:
        return [1, 2]

    def check_broken() -> list:
        raise KeyError("station_abbr")

    assert smoke_test.run([check_ok, check_broken]) == 1
    out = capsys.readouterr().out
    assert "✗ check_broken" in out
    assert "1/2 checks passed" in out
