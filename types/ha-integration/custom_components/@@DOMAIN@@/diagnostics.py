"""Diagnostics for @@NAME@@ (Settings -> Devices & services -> ⋮ -> Download diagnostics).

Users attach this file to bug reports, and bug reports are public: every
secret and everything that locates the user is redacted. Add new keys to
``TO_REDACT`` in the same PR that stores them.
"""

from __future__ import annotations

from dataclasses import asdict, is_dataclass
from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.const import (
    CONF_API_KEY,
    CONF_HOST,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import HomeAssistant

from .const import VERSION
from .coordinator import IntegrationConfigEntry

TO_REDACT = {
    CONF_API_KEY,
    CONF_HOST,
    CONF_LATITUDE,
    CONF_LONGITUDE,
    CONF_PASSWORD,
    CONF_TOKEN,
    CONF_USERNAME,
    "serial",
    "serial_number",
    "unique_id",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: IntegrationConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator = entry.runtime_data.coordinator
    data = coordinator.data
    # async_redact_data only walks dicts and lists; a dataclass would slip
    # through unredacted.
    if is_dataclass(data) and not isinstance(data, type):
        data = asdict(data)
    return async_redact_data(
        {
            "version": VERSION,
            "entry": {
                "title": entry.title,
                "unique_id": entry.unique_id,
                "data": dict(entry.data),
                "options": dict(entry.options),
            },
            "coordinator": {
                "last_update_success": coordinator.last_update_success,
                "last_exception": (
                    repr(coordinator.last_exception)
                    if coordinator.last_exception
                    else None
                ),
                "update_interval": str(coordinator.update_interval),
                "data": data,
            },
        },
        TO_REDACT,
    )
