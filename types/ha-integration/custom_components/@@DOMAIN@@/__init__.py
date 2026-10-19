"""The @@NAME@@ integration."""

from __future__ import annotations

from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .coordinator import IntegrationConfigEntry, IntegrationCoordinator, IntegrationData

# Platforms are added by the issues that implement them.
PLATFORMS: list[Platform] = []


async def async_setup_entry(hass: HomeAssistant, entry: IntegrationConfigEntry) -> bool:
    """Set up @@NAME@@ from a config entry."""
    coordinator = IntegrationCoordinator(hass, entry)
    # An upstream service that does not answer at startup is a temporary
    # problem: this raises ConfigEntryNotReady and HA retries with back-off.
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = IntegrationData(coordinator=coordinator)

    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(
    hass: HomeAssistant, entry: IntegrationConfigEntry
) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)


async def _async_update_listener(
    hass: HomeAssistant, entry: IntegrationConfigEntry
) -> None:
    """Reload the entry so changed options take effect."""
    await hass.config_entries.async_reload(entry.entry_id)
