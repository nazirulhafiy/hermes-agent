from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from gateway.config import PlatformConfig
from gateway.platforms import discord as discord_platform
from gateway.platforms.discord import DiscordAdapter


@pytest.mark.asyncio
async def test_discord_disconnect_clears_typing_tasks(monkeypatch):
    """Discord disconnect must not leave persistent typing loops behind."""
    monkeypatch.setattr(
        discord_platform.discord,
        "http",
        SimpleNamespace(Route=lambda method, path, **kwargs: (method, path, kwargs)),
        raising=False,
    )

    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="fake-token"))
    client = SimpleNamespace(
        http=SimpleNamespace(request=AsyncMock(return_value=None)),
        close=AsyncMock(return_value=None),
    )
    adapter._client = client

    await adapter.send_typing("123")
    task = adapter._typing_tasks["123"]

    await adapter.disconnect()

    assert adapter._typing_tasks == {}
    assert task.cancelled() or task.done()
    client.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_discord_cancel_background_tasks_clears_typing_tasks(monkeypatch):
    """Gateway shutdown cleanup must drain Discord-specific typing loops."""
    monkeypatch.setattr(
        discord_platform.discord,
        "http",
        SimpleNamespace(Route=lambda method, path, **kwargs: (method, path, kwargs)),
        raising=False,
    )

    adapter = DiscordAdapter(PlatformConfig(enabled=True, token="fake-token"))
    adapter._client = SimpleNamespace(http=SimpleNamespace(request=AsyncMock(return_value=None)))

    await adapter.send_typing("123")
    task = adapter._typing_tasks["123"]

    await adapter.cancel_background_tasks()

    assert adapter._typing_tasks == {}
    assert task.cancelled() or task.done()
