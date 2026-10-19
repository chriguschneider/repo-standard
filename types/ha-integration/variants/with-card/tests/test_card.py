"""The bundled card: served, loaded on dashboards, and still there after a reload."""

from __future__ import annotations

from http import HTTPStatus
from pathlib import Path

from homeassistant.components.frontend import DATA_EXTRA_MODULE_URL
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.@@DOMAIN@@ import CARD_FILENAME, CARD_URL
from custom_components.@@DOMAIN@@.const import VERSION


def _module_urls(hass: HomeAssistant) -> frozenset[str]:
    return hass.data[DATA_EXTRA_MODULE_URL].urls


async def test_card_survives_reload_and_leaves_on_unload(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_upstream
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    assert CARD_URL in _module_urls(hass)

    # A reload unloads (removes the URL) and sets up again (adds it back);
    # registering the static path a second time would fail the setup.
    assert await hass.config_entries.async_reload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert config_entry.state is ConfigEntryState.LOADED
    assert CARD_URL in _module_urls(hass)

    assert await hass.config_entries.async_unload(config_entry.entry_id)
    await hass.async_block_till_done()
    assert CARD_URL not in _module_urls(hass)


async def test_card_file_is_served(
    hass: HomeAssistant, hass_client, config_entry: MockConfigEntry, mock_upstream
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    client = await hass_client()
    response = await client.get(CARD_URL)
    assert response.status == HTTPStatus.OK
    body = await response.text()
    assert f"CARD_VERSION = '{VERSION}'" in body
    assert CARD_URL.endswith(f"{CARD_FILENAME}?v={VERSION}")


def test_release_zip_carries_the_frontend() -> None:
    """HACS installs the zip, so the card must be in it."""
    root = Path(__file__).resolve().parent.parent
    release = (root / ".github" / "workflows" / "release.yml").read_text(
        encoding="utf-8"
    )
    # Zipped recursively from the integration directory, then checked to hold
    # exactly its tracked files: frontend/ cannot go missing.
    assert 'zip -r -X "$GITHUB_WORKSPACE/@@DOMAIN@@.zip" .' in release
    assert "git ls-files" in release
    component = root / "custom_components" / "@@DOMAIN@@"
    assert (component / "frontend" / CARD_FILENAME).is_file()
