## Installation

### HACS (recommended)

1. Click **Open in HACS** above, or in HACS → ⋮ → *Custom repositories* add
   `https://github.com/@@OWNER@@/@@REPO@@` as type *Dashboard*.
2. Download **@@NAME@@**. HACS registers the resource for you.
3. Edit a dashboard → **Add card** → *@@NAME@@*.

### Manual

Copy `dist/@@DOMAIN@@.js` to `config/www/` and add it as a resource
(`/local/@@DOMAIN@@.js`, type *JavaScript module*).

## Configuration

The card has a visual editor; everything it offers can also be set in YAML.

```yaml
type: custom:@@DOMAIN@@
entity: sensor.example
title: @@NAME@@
```

| Option | Default | Description |
|---|---|---|
| `entity` | *(required)* | Entity whose state the card shows. |
| `title` | none | Card header. |
| `show_state` | `true` | Show the entity's state (otherwise its ID). |

TODO(repo-standard): replace with the card's real options, defaults from `src/const.ts`.

<!-- Screenshots: HACS renders this README as it was at the release tag and
strips <picture> and relative paths. Use plain <img> with absolute
https://raw.githubusercontent.com/@@OWNER@@/@@REPO@@/@@BRANCH@@/... URLs and
never rename an image once released. -->
