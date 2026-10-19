"""Constants for @@NAME@@."""

from __future__ import annotations

DOMAIN = "@@DOMAIN@@"
# Keep in sync with manifest.json (guarded by tests/test_metadata.py).
VERSION = "0.0.1"

# Options (Settings -> Devices & services -> @@NAME@@ -> Configure).
CONF_UPDATE_INTERVAL = "update_interval"
DEFAULT_UPDATE_INTERVAL = 30  # minutes
MIN_UPDATE_INTERVAL = 5
MAX_UPDATE_INTERVAL = 1440
