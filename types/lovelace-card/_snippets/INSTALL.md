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

```yaml
type: custom:@@DOMAIN@@
title: @@NAME@@
```

TODO(repo-standard): all options with defaults.
