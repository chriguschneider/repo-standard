"""Base entity: one device per config entry, availability from the data."""

from __future__ import annotations

from homeassistant.const import CONF_HOST
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import IntegrationCoordinator


class IntegrationEntity(CoordinatorEntity[IntegrationCoordinator]):
    """Shared device info and availability for every entity of a device."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: IntegrationCoordinator, key: str) -> None:
        super().__init__(coordinator)
        entry = coordinator.config_entry
        # The config flow always sets the serial number as the unique id.
        serial = entry.unique_id or entry.entry_id
        self._attr_unique_id = f"{serial}_{key}"
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, serial)},
            name=entry.title,
            serial_number=serial,
            configuration_url=f"http://{entry.data[CONF_HOST]}/",
        )

    @property
    def available(self) -> bool:
        """Available while there is a reading to show.

        Not ``last_update_success``: a device that is switched off keeps its
        last state instead of blanking every card, and one that was off at
        startup is unavailable until its first reading.
        """
        return self.coordinator.data is not None
