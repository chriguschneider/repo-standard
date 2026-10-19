"""Client for the device's local HTTP API.

Pure Python: no Home Assistant imports, so it can be tested without HA and
reused elsewhere (label ``area-client``). The config flow and the
coordinator only see ``DeviceInfo``, ``DeviceState`` and the two errors.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=10)


class CannotConnect(Exception):
    """Nothing answered: the device is off, the host is wrong, or the LAN is."""


class NotSupported(Exception):
    """Something answered, but it is not a device this integration supports."""


@dataclass(frozen=True)
class DeviceInfo:
    """What the device says about itself; ``serial`` is the unique id."""

    serial: str
    name: str
    model: str | None = None
    firmware: str | None = None


@dataclass(frozen=True)
class DeviceState:
    """One reading of the device."""

    status: str


class DeviceClient:
    """Talk to one device at ``host``."""

    # TODO(repo-standard): replace the endpoints and fields below with the
    # device's real API, cite it in docs/upstream.md, and cut the fixtures in
    # tests/fixtures/ from real responses.

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self._host = host

    async def _get_json(self, path: str) -> dict[str, Any]:
        url = f"http://{self._host}/{path}"
        try:
            async with self._session.get(url, timeout=TIMEOUT) as resp:
                resp.raise_for_status()
                payload = await resp.json(content_type=None)
        except aiohttp.ClientResponseError as err:
            # It answered with an HTTP error: a web server, not our device.
            raise NotSupported(f"{url}: HTTP {err.status}") from err
        except (aiohttp.ClientError, TimeoutError) as err:
            raise CannotConnect(f"{url}: {err!r}") from err
        except ValueError as err:
            raise NotSupported(f"{url}: not JSON") from err
        if not isinstance(payload, dict):
            raise NotSupported(f"{url}: unexpected payload {type(payload).__name__}")
        return payload

    async def async_probe(self) -> DeviceInfo:
        """Identify the device; raises CannotConnect or NotSupported."""
        data = await self._get_json("info")
        serial = data.get("serial")
        if not isinstance(serial, str) or not serial:
            raise NotSupported("no serial number in the info response")
        return DeviceInfo(
            serial=serial,
            name=str(data.get("name") or serial),
            model=data.get("model"),
            firmware=data.get("firmware"),
        )

    async def async_get_state(self) -> DeviceState:
        """Read the current state; raises CannotConnect or NotSupported."""
        data = await self._get_json("state")
        status = data.get("status")
        if not isinstance(status, str):
            raise NotSupported("no status in the state response")
        return DeviceState(status=status)


async def async_probe(session: aiohttp.ClientSession, host: str) -> DeviceInfo:
    """Identify the device at ``host`` (used by the config flow)."""
    return await DeviceClient(session, host).async_probe()
