### Home Assistant pitfalls

Lessons from real integrations; several shipped with every test green.

- **`vol.Required` with an empty-string default blocks the form.** The UI
  treats `""` as "not filled in" and refuses to submit, while a test that
  calls `async_configure` with a value passes. Use `vol.Optional` for
  fields that may stay empty, or a real default; give a required field no
  default at all.
- **Open cards only see what the coordinator announces.** A dashboard card
  re-renders when the entity it watches writes a new state, and coordinator
  entities only write state when the coordinator calls its listeners. Data
  that changes outside `_async_update_data` (a forecast, a service call, a
  push message) must go through `coordinator.async_set_updated_data(...)`
  or `coordinator.async_update_listeners()`; changing an attribute and
  waiting does nothing for an open card.
- **Availability follows the data, not the last poll.** An entity is
  available when the coordinator has data it can show
  (`coordinator.data is not None`), not only when the last update
  succeeded. One failed poll must not blank every card; data that is too
  old to trust is the entity's call, made explicitly.
- **Never block the event loop.** No synchronous I/O, and no parsing of big
  CSV/JSON payloads on the loop: `await hass.async_add_executor_job(parse,
  payload)`. HA logs "Detected blocking call" and the whole UI stalls.
- **Diagnostics redact secrets and location.** Users attach the diagnostics
  file to public issues. Everything in `diagnostics.py` goes through
  `async_redact_data`; API keys, tokens, passwords, coordinates, postal
  codes, hosts and serial numbers are in `TO_REDACT`, and
  `tests/test_diagnostics.py` proves it. A new stored field that identifies
  the user is added to `TO_REDACT` in the same PR.
@@DEVICE_RULES@@@@SMOKE_RULES@@@@CARD_RULES@@
