"""A switched-off device is normal: setup succeeds, entities follow the data."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import STATE_UNAVAILABLE
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.@@DOMAIN@@.client import CannotConnect
from custom_components.@@DOMAIN@@.const import DOMAIN

from .conftest import device_state


def _status_entity(hass: HomeAssistant, entry: MockConfigEntry) -> str:
    entity_id = er.async_get(hass).async_get_entity_id(
        "sensor", DOMAIN, f"{entry.unique_id}_status"
    )
    assert entity_id
    return entity_id


async def test_setup_succeeds_while_device_is_off(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_upstream
) -> None:
    mock_upstream.side_effect = CannotConnect("off")
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()

    assert config_entry.state is ConfigEntryState.LOADED  # no ConfigEntryNotReady
    entity_id = _status_entity(hass, config_entry)
    assert hass.states.get(entity_id).state == STATE_UNAVAILABLE

    # Switched on: the next poll fills the entity in.
    mock_upstream.side_effect = None
    await config_entry.runtime_data.coordinator.async_refresh()
    await hass.async_block_till_done()
    assert hass.states.get(entity_id).state == device_state().status


async def test_entity_keeps_last_state_when_device_goes_off(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_upstream
) -> None:
    assert await hass.config_entries.async_setup(config_entry.entry_id)
    await hass.async_block_till_done()
    entity_id = _status_entity(hass, config_entry)
    assert hass.states.get(entity_id).state == device_state().status

    mock_upstream.side_effect = CannotConnect("off")
    coordinator = config_entry.runtime_data.coordinator
    await coordinator.async_refresh()
    await hass.async_block_till_done()

    assert coordinator.last_update_success is False
    assert hass.states.get(entity_id).state == device_state().status
