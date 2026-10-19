"""Data update coordinator for @@NAME@@.

One coordinator per config entry fetches the upstream data on a schedule;
entities read ``coordinator.data`` and are told about new data through the
coordinator's listeners.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class IntegrationData:
    """Everything a loaded entry needs, stored on ``entry.runtime_data``."""

    coordinator: IntegrationCoordinator


type IntegrationConfigEntry = ConfigEntry[IntegrationData]


class IntegrationCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetch the upstream data for one config entry."""

    config_entry: IntegrationConfigEntry

    def __init__(self, hass: HomeAssistant, entry: IntegrationConfigEntry) -> None:
        minutes = entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=DOMAIN,
            update_interval=timedelta(minutes=minutes),
        )

    async def _async_update_data(self) -> dict[str, Any]:
        # TODO(repo-standard): fetch from the upstream client (pure Python, no
        # HA imports) and raise UpdateFailed on errors. Parse big CSV/JSON
        # payloads in the executor: `await self.hass.async_add_executor_job(...)`.
        return {}
