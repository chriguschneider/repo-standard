# Upstream facts

Measured facts about every external system this repo talks to: endpoints,
file formats, units, update cadence, limits, quirks. Agents read this file
before they touch anything that depends on an upstream, and every lookup
table or constant in the code cites a line here, a URL or a fixture.

Write what you **measured**, with the date and how (command, file), not what
a documentation page promises. When the upstream changes, add a dated entry
instead of rewriting history.

TODO(repo-standard): one section per upstream, or delete this file if the
repo has none.

## <Upstream name>

- **Measured:** YYYY-MM-DD, how
- **Endpoint / file:** ...
- **Format and units:** ...
- **Cadence and limits:** ...
- **Quirks:** ...
