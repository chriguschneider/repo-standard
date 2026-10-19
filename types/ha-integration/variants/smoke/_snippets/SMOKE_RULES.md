
### Upstream smoke test

`.github/workflows/smoke-test.yml` runs `tests/tools/smoke_test.py` against
the live upstream every week. On failure it opens or comments on one issue
titled "Upstream smoke test failed" (label `tracking`, never a P-label); on
recovery it comments and leaves the issue open for a human to close.

- Add a check to `CHECKS` in the same PR that starts parsing a new upstream
  endpoint. Checks validate shape (headers, field names, plausible ranges),
  not content; no data at all is a pass.
- The script stays stdlib-only and secret-free.
- A failing smoke test is not a reason to change the parser blindly: first
  compare what upstream returns now with `docs/upstream.md`, then refresh
  the fixtures from the new real files.
