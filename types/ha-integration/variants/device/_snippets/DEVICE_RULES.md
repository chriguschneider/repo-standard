
### Local devices

- **One entry per device, keyed by its serial number.** The config flow
  probes the host, sets the serial as the unique id and calls
  `_abort_if_unique_id_configured(updates={CONF_HOST: host})`, so adding a
  device again under a new IP address fixes the existing entry instead of
  creating a second one. Never key on the host: DHCP changes it.
- **Switched off is not an error.** Setup succeeds without the device
  (`coordinator.async_refresh()`, not `async_config_entry_first_refresh()`,
  which raises ConfigEntryNotReady and retries forever). Entities are
  unavailable until the first reading, then keep the last one.
- **`client.py` has no Home Assistant imports.** It speaks the device's
  protocol and raises `CannotConnect` (nothing answered) or `NotSupported`
  (something answered, but not this device); the config flow maps them to
  the `cannot_connect` / `not_supported` errors.
