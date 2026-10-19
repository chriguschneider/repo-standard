"""The device client, without Home Assistant: HTTP replayed by aioresponses."""

from __future__ import annotations

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.@@DOMAIN@@.client import (
    CannotConnect,
    DeviceClient,
    NotSupported,
    async_probe,
)

from .conftest import HOST, device_info, device_state, load_fixture

BASE = f"http://{HOST}"


async def test_probe_reads_the_info_response() -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE}/info", payload=load_fixture("info.json"))
        async with aiohttp.ClientSession() as session:
            assert await async_probe(session, HOST) == device_info()


async def test_state_reads_the_state_response() -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE}/state", payload=load_fixture("state.json"))
        async with aiohttp.ClientSession() as session:
            client = DeviceClient(session, HOST)
            assert await client.async_get_state() == device_state()


async def test_no_answer_is_cannot_connect() -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE}/info", exception=aiohttp.ClientConnectionError("off"))
        async with aiohttp.ClientSession() as session:
            with pytest.raises(CannotConnect):
                await async_probe(session, HOST)


async def test_timeout_is_cannot_connect() -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE}/info", exception=TimeoutError())
        async with aiohttp.ClientSession() as session:
            with pytest.raises(CannotConnect):
                await async_probe(session, HOST)


@pytest.mark.parametrize(
    "response",
    [
        {"status": 404},
        {"body": "<html>router login</html>"},
        {"payload": ["not", "an", "object"]},
        {"payload": {"name": "no serial"}},
    ],
)
async def test_something_else_is_not_supported(response: dict) -> None:
    with aioresponses() as mock:
        mock.get(f"{BASE}/info", **response)
        async with aiohttp.ClientSession() as session:
            with pytest.raises(NotSupported):
                await async_probe(session, HOST)
