"""Shared pytest fixtures.

``enable_custom_integrations`` (autouse) makes every test that requests the
``hass`` fixture load the custom component from the repo tree. Tests that
do not use ``hass`` (pure-Python and metadata tests) are unaffected.
"""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.@@DOMAIN@@.const import DOMAIN


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/ from this repo in every hass test."""
    return


@pytest.fixture
def config_entry(hass) -> MockConfigEntry:
    """A config entry as the config flow creates it, added but not set up."""
    entry = MockConfigEntry(domain=DOMAIN, title="@@NAME@@", data={})
    entry.add_to_hass(hass)
    return entry


@pytest.fixture
def mock_upstream() -> Iterator[None]:
    """Replace every upstream call the coordinator makes.

    The scaffold's coordinator calls nothing yet. Once it has a client, patch
    it here (replaying trimmed real files from tests/fixtures/), so every
    test that sets up an entry stays off the network.
    """
    yield
