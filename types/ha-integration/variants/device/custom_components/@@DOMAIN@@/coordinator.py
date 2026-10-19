"""Data update coordinator for @@NAME@@.

One coordinator per device polls the local API; entities read
``coordinator.data`` and are told about new data through the coordinator's
listeners.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import timedelta

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .client import CannotConnect, DeviceClient, DeviceState, NotSupported
from .const import CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL, DOMAIN

_LOGGER = logging.getLogger(__name__)


@dataclass
class IntegrationData:
    """Everything a loaded entry needs, stored on ``entry.runtime_data``."""

    coordinator: IntegrationCoordinator


type IntegrationConfigEntry = ConfigEntry[IntegrationData]


class IntegrationCoordinator(DataUpdateCoordinator[DeviceState]):
    """Poll one device on the LAN."""

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
        self.client = DeviceClient(async_get_clientsession(hass), entry.data[CONF_HOST])

    async def _async_update_data(self) -> DeviceState:
        try:
            return await self.client.async_get_state()
        except (CannotConnect, NotSupported) as err:
            # Keeps the last reading in self.data; entities stay available
            # with it (entity.py) until the device answers again.
            raise UpdateFailed(str(err)) from err
