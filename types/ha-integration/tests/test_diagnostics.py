"""Diagnostics are downloadable and leak no secret or location."""

from __future__ import annotations

import json

from homeassistant.components.diagnostics import REDACTED
from homeassistant.const import CONF_API_KEY, CONF_LATITUDE, CONF_LONGITUDE
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.components.diagnostics import (
    get_diagnostics_for_config_entry,
)

SECRET = "s3cr3t-api-key"


async def test_diagnostics_redact_secrets_and_location(
    hass: HomeAssistant,
    hass_client,
    config_entry: MockConfigEntry,
    mock_upstream,
) -> None:
    hass.config_entries.async_update_entry(
        config_entry,
        data={
            **config_entry.data,
            CONF_API_KEY: SECRET,
            CONF_LATITUDE: 46.948,
            CONF_LONGITUDE: 7.447,
        },
    )
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await get_diagnostics_for_config_entry(hass, hass_client, config_entry)

    data = result["entry"]["data"]
    assert data[CONF_API_KEY] == REDACTED
    assert data[CONF_LATITUDE] == REDACTED
    assert data[CONF_LONGITUDE] == REDACTED
    dumped = json.dumps(result)
    assert SECRET not in dumped
    assert "46.948" not in dumped
    assert "coordinator" in result
