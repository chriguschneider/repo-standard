"""The @@NAME@@ integration, with its own dashboard card."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.frontend import add_extra_js_url, remove_extra_js_url
from homeassistant.components.http import StaticPathConfig
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import DOMAIN, VERSION
from .coordinator import IntegrationConfigEntry, IntegrationCoordinator, IntegrationData

# Platforms are added by the issues that implement them.
PLATFORMS: list[Platform] = []

CARD_FILENAME = "@@CARD_TAG@@.js"
CARD_URL_BASE = f"/{DOMAIN}/frontend"
# The file is read from disk on every request; ?v= makes browsers fetch it
# again after an update instead of running a cached old card.
CARD_URL = f"{CARD_URL_BASE}/{CARD_FILENAME}?v={VERSION}"
_STATIC_PATH_REGISTERED = f"{DOMAIN}_card_static_path"


async def async_setup_entry(hass: HomeAssistant, entry: IntegrationConfigEntry) -> bool:
    """Set up @@NAME@@ from a config entry."""
    # Before the first refresh: while upstream is down the card still loads
    # and shows the entities as unavailable instead of "custom element
    # doesn't exist". async_on_unload also runs when setup is retried.
    await _async_register_card(hass)
    entry.async_on_unload(lambda: remove_extra_js_url(hass, CARD_URL))

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


async def _async_register_card(hass: HomeAssistant) -> None:
    """Serve frontend/ and load the card on every dashboard.

    HA cannot unregister a static path and registering one twice raises, so
    the path is added once per HA run. The module URL is added on every setup
    and removed on every unload, so a reload neither loses nor doubles it.
    """
    if not hass.data.get(_STATIC_PATH_REGISTERED):
        await hass.http.async_register_static_paths(
            [
                StaticPathConfig(
                    CARD_URL_BASE,
                    str(Path(__file__).parent / "frontend"),
                    cache_headers=False,
                )
            ]
        )
        hass.data[_STATIC_PATH_REGISTERED] = True
    add_extra_js_url(hass, CARD_URL)


async def _async_update_listener(
    hass: HomeAssistant, entry: IntegrationConfigEntry
) -> None:
    """Reload the entry so changed options take effect."""
    await hass.config_entries.async_reload(entry.entry_id)
