"""Shared pytest fixtures.

``enable_custom_integrations`` (autouse) makes every test that requests the
``hass`` fixture load the custom component from the repo tree. Tests that
do not use ``hass`` (pure-Python and metadata tests) are unaffected.
"""

from __future__ import annotations

import pytest


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    """Load custom_components/ from this repo in every hass test."""
    return
