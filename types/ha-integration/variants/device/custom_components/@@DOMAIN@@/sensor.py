"""Sensors for @@NAME@@."""

from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import IntegrationConfigEntry, IntegrationCoordinator
from .entity import IntegrationEntity


async def async_setup_entry(
    hass: HomeAssistant,
    entry: IntegrationConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Add the device's sensors."""
    async_add_entities([StatusSensor(entry.runtime_data.coordinator)])


class StatusSensor(IntegrationEntity, SensorEntity):
    """What the device reports it is doing."""

    _attr_translation_key = "status"

    def __init__(self, coordinator: IntegrationCoordinator) -> None:
        super().__init__(coordinator, "status")

    @property
    def native_value(self) -> str | None:
        data = self.coordinator.data
        return data.status if data else None
