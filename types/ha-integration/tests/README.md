# Tests

## How to run

```
pip install -r requirements_test.txt
ruff check custom_components tests
pytest -q
```

Integration tests use `pytest-homeassistant-custom-component` (`hass`
fixture). Every test that sets up an entry requests `mock_upstream`
(`tests/conftest.py`), so the suite never touches the network.

## Fixtures

Upstream responses are replayed from `tests/fixtures/`. Fixtures are
**trimmed real files**, never hand-written:

- Keep the real header, column order, encoding and separator (a Latin-1,
  `;`-separated CSV stays exactly that; a JSON keeps its real nesting).
- Keep a handful of rows: enough for every code path a test exercises,
  including the odd ones (an empty value, a missing station, a gap).
- Stay under **~50 KB** per file. Cut rows, not columns.
- Add a row to the table below in the same PR: where the file was cut from,
  when, and what was kept. A fixture nobody can trace back cannot be
  refreshed when upstream changes.

| Fixture | Cut from (URL or device endpoint) | Date | What was kept |
|---|---|---|---|
| _none yet_ | | | |

Optional: a stdlib-only `tests/tools/refresh_fixtures.py` that fetches the
live files and trims them the same way, so a refresh is one command and a
reviewed diff.
