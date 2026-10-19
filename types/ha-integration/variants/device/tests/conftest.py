"""Shared pytest fixtures.

``enable_custom_integrations`` (autouse) makes every test that requests the
``hass`` fixture load the custom component from the repo tree. Tests that
do not use ``hass`` (pure-Python and metadata tests) are unaffected.
"""

from __future__ import annotations

import json
from collections.abc import Iterator
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.@@DOMAIN@@.client import DeviceInfo, DeviceState
from custom_components.@@DOMAIN@@.const import DOMAIN

FIXTURES = Path(__file__).parent / "fixtures"
HOST = "192.0.2.10"  # TEST-NET-1, never routable


def load_fixture(name: str) -> dict[str, Any]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def device_info(**overrides: Any) -> DeviceInfo:
    return DeviceInfo(**{**load_fixture("info.json"), **overrides})


def device_state() -> DeviceState:
    return DeviceState(**load_fixture("state.json"))


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/ from this repo in every hass test."""
    return


@pytest.fixture
def config_entry(hass) -> MockConfigEntry:
    """A config entry as the config flow creates it, added but not set up."""
    info = device_info()
    entry = MockConfigEntry(
        domain=DOMAIN, title=info.name, unique_id=info.serial, data={CONF_HOST: HOST}
    )
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_upstream() -> Iterator[AsyncMock]:
    """The device answers with the state fixture; set side_effect to switch it off."""
    with patch(
        "custom_components.@@DOMAIN@@.coordinator.DeviceClient.async_get_state",
        return_value=device_state(),
    ) as get_state:
        yield get_state


@pytest.fixture
def mock_probe() -> Iterator[AsyncMock]:
    """The config flow's probe; returns the info fixture unless told otherwise."""
    with patch(
        "custom_components.@@DOMAIN@@.config_flow.async_probe",
        return_value=device_info(),
    ) as probe:
        yield probe
