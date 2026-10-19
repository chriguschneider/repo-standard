"""Options: open, submit, stored, and the entry reloads to apply them."""

from __future__ import annotations

from datetime import timedelta

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType, InvalidData
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.@@DOMAIN@@.const import CONF_UPDATE_INTERVAL


async def test_options_update_and_reload(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_upstream
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    before = config_entry.runtime_data

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "init"

    result = await hass.config_entries.options.async_configure(
        result["flow_id"], {CONF_UPDATE_INTERVAL: 15}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    await hass.async_block_till_done()

    assert config_entry.options == {CONF_UPDATE_INTERVAL: 15}
    # The update listener reloaded the entry: new runtime data, new interval.
    assert config_entry.state is ConfigEntryState.LOADED
    assert config_entry.runtime_data is not before
    assert config_entry.runtime_data.coordinator.update_interval == timedelta(
        minutes=15
    )


async def test_options_reject_out_of_range(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_upstream
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    result = await hass.config_entries.options.async_init(config_entry.entry_id)
    with pytest.raises(InvalidData):
        await hass.config_entries.options.async_configure(
            result["flow_id"], {CONF_UPDATE_INTERVAL: 1}
        )
    assert config_entry.options == {}
