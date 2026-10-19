"""Live smoke test against the real upstream (weekly, smoke-test.yml).

Run from the repo root:

    python tests/tools/smoke_test.py

Stdlib only, so the workflow needs no install. Each check fetches live data
and validates its *shape* (headers, field names, plausible values), not its
content. A check that gets no data back passes: an empty forecast window or
a quiet station is normal, and a false alarm every few weeks would train
everyone to ignore the issue.

Until CHECKS has an entry this script passes with a notice. Fill it in:

    def check_stations() -> list:
        rows = fetch_csv("https://.../stations.csv")
        assert rows[0].keys() >= {"station_abbr", "lat", "lon"}, rows[0].keys()
        return rows

    CHECKS = [check_stations]

Exit status 0 when every check passes, 1 when any raises.
"""

from __future__ import annotations

import csv
import io
import json
import sys
import urllib.request
from collections.abc import Callable, Sized
from typing import Any

TIMEOUT = 30
USER_AGENT = "@@REPO@@-smoke-test (+https://github.com/@@OWNER@@/@@REPO@@)"


def fetch(url: str) -> bytes:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=TIMEOUT) as response:  # noqa: S310
        return response.read()


def fetch_json(url: str) -> Any:
    return json.loads(fetch(url).decode("utf-8"))


def fetch_csv(url: str, encoding: str = "utf-8", delimiter: str = ";") -> list[dict]:
    text = fetch(url).decode(encoding)
    return list(csv.DictReader(io.StringIO(text), delimiter=delimiter))


# TODO(repo-standard): one function per upstream endpoint the integration
# parses; each returns what it fetched (empty is fine) or raises.
CHECKS: list[Callable[[], Sized | None]] = []


def run(checks: list[Callable[[], Sized | None]]) -> int:
    if not checks:
        print("No smoke checks defined yet (tests/tools/smoke_test.py, CHECKS).")
        print("Passing: there is nothing to check. Fill CHECKS in.")
        return 0

    failed = 0
    for check in checks:
        name = check.__name__
        try:
            result = check()
        except Exception as err:  # noqa: BLE001 -- report every failure
            failed += 1
            print(f"✗ {name}: {type(err).__name__}: {err}")
            continue
        if not result:
            print(f"✓ {name}: no data right now (counts as a pass)")
        else:
            print(f"✓ {name}: {len(result)} item(s)")

    print()
    print(f"{len(checks) - failed}/{len(checks)} checks passed")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(run(CHECKS))
