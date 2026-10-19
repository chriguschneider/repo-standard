"""Config and options flow for @@NAME@@."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    OptionsFlow,
)
from homeassistant.const import CONF_HOST
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .client import CannotConnect, NotSupported, async_probe
from .const import (
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MAX_UPDATE_INTERVAL,
    MIN_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

# No default for the host: a required field with an empty-string default
# cannot be submitted in the UI (AGENTS.md, Home Assistant pitfalls).
USER_SCHEMA = vol.Schema({vol.Required(CONF_HOST): str})


class IntegrationConfigFlow(ConfigFlow, domain=DOMAIN):
    """Add one device by host; one entry per device (serial number)."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                info = await async_probe(async_get_clientsession(self.hass), host)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except NotSupported:
                errors["base"] = "not_supported"
            except Exception:
                _LOGGER.exception("Unexpected error probing %s", host)
                errors["base"] = "unknown"
            else:
                await self.async_set_unique_id(info.serial)
                # The same device under a new address (DHCP): update the
                # host of the existing entry instead of adding a second one.
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                return self.async_create_entry(
                    title=info.name, data={CONF_HOST: host}
                )

        return self.async_show_form(
            step_id="user",
            data_schema=self.add_suggested_values_to_schema(USER_SCHEMA, user_input),
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(config_entry: ConfigEntry) -> OptionsFlow:
        """Return the options flow."""
        return IntegrationOptionsFlow()


class IntegrationOptionsFlow(OptionsFlow):
    """Change options after setup; the update listener reloads the entry."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        current = self.config_entry.options.get(
            CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL
        )
        schema = vol.Schema(
            {
                vol.Required(CONF_UPDATE_INTERVAL, default=current): vol.All(
                    vol.Coerce(int),
                    vol.Range(min=MIN_UPDATE_INTERVAL, max=MAX_UPDATE_INTERVAL),
                ),
            }
        )
        return self.async_show_form(step_id="init", data_schema=schema)
