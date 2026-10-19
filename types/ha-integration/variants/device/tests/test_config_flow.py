"""Adding a device: probe, errors, one entry per serial number."""

from __future__ import annotations

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.@@DOMAIN@@.client import CannotConnect, NotSupported
from custom_components.@@DOMAIN@@.const import DOMAIN

from .conftest import HOST, device_info


async def _start(hass: HomeAssistant):
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "user"
    return result


async def test_user_flow_creates_entry(
    hass: HomeAssistant, mock_probe, mock_upstream
) -> None:
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: f" {HOST} "}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == device_info().name
    assert result["data"] == {CONF_HOST: HOST}
    assert result["result"].unique_id == device_info().serial
    mock_probe.assert_awaited_once()


async def test_same_serial_updates_host_and_aborts(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_probe, mock_upstream
) -> None:
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.99"}
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert config_entry.data[CONF_HOST] == "192.0.2.99"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 1


async def test_cannot_connect_shows_error(
    hass: HomeAssistant, mock_probe, mock_upstream
) -> None:
    mock_probe.side_effect = CannotConnect("off")
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "cannot_connect"}

    # Once the device is on, the same form goes through.
    mock_probe.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY


async def test_not_supported_shows_error(
    hass: HomeAssistant, mock_probe, mock_upstream
) -> None:
    mock_probe.side_effect = NotSupported("a printer")
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: HOST}
    )
    assert result["type"] is FlowResultType.FORM
    assert result["errors"] == {"base": "not_supported"}


async def test_second_device_is_allowed(
    hass: HomeAssistant, config_entry: MockConfigEntry, mock_probe, mock_upstream
) -> None:
    mock_probe.return_value = device_info(serial="E5F6A7B8", name="Second device")
    result = await _start(hass)
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.0.2.11"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "E5F6A7B8"
    assert len(hass.config_entries.async_entries(DOMAIN)) == 2
