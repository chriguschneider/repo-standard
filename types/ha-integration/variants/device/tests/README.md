# Tests

## How to run

```
pip install -r requirements_test.txt
ruff check custom_components tests
pytest -q
```

Integration tests use `pytest-homeassistant-custom-component` (`hass`
fixture). The device never answers for real: `mock_upstream` patches the
coordinator's `DeviceClient.async_get_state` and `mock_probe` the config
flow's probe (`tests/conftest.py`); `tests/test_client.py` replays HTTP with
`aioresponses`. Set `side_effect = CannotConnect(...)` to switch the device
off.

## Fixtures

Device responses are replayed from `tests/fixtures/`. Fixtures are
**trimmed real files**, never hand-written:

- Keep the real structure, field names, encoding and quirks of what the
  device sends (an HTML status page stays HTML; a JSON keeps its nesting).
- Keep enough for every code path a test exercises, including the odd ones
  (a missing field, an error state).
- Stay under **~50 KB** per file.
- Add a row to the table below in the same PR: the endpoint, the firmware,
  the date, and what was kept.

| Fixture | Cut from (device endpoint, firmware) | Date | What was kept |
|---|---|---|---|
| `info.json` | TODO(repo-standard): placeholder, replace with a real `/info` response | | |
| `state.json` | TODO(repo-standard): placeholder, replace with a real `/state` response | | |

Optional: a stdlib-only `tests/tools/refresh_fixtures.py` that fetches the
live responses from a device on your LAN and trims them the same way.
