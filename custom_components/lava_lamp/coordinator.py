"""Coordinator for lava lamp SSE and polling updates."""

from __future__ import annotations

import asyncio
import json
import logging

from aiohttp import ClientError, ClientSession, ClientTimeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    DOMAIN,
    ERROR_LOG_INTERVAL,
    FAST_POLL_INTERVAL,
    HEARTBEAT_TIMEOUT,
    INITIAL_ERROR_BACKOFF,
    MAX_ERROR_BACKOFF,
    OFFLINE_POLL_INTERVAL,
    SSE_RETRY_INTERVAL,
)
from .models import LavaLampState

LOGGER = logging.getLogger(__name__)
SSE_REJECTED_STATUSES = {429, 503}


class SSERejectedError(Exception):
    """Raised when the API rejects the SSE connection."""


class LavaLampCoordinator(DataUpdateCoordinator[LavaLampState | None]):
    """Owns lava lamp connection state and entity updates."""

    def __init__(
        self,
        hass: HomeAssistant,
        base_url: str,
        emit_delay_seconds: float = 0.0,
    ) -> None:
        super().__init__(hass, LOGGER, name=DOMAIN, update_method=self._async_update_data)
        self.base_url = base_url.rstrip("/")
        self.emit_delay_seconds = float(emit_delay_seconds)
        if self.emit_delay_seconds < 0:
            raise ValueError("emit_delay_seconds must be non-negative")
        self.session: ClientSession = async_get_clientsession(hass)
        self._task: asyncio.Task[None] | None = None
        self._publisher_task: asyncio.Task[None] | None = None
        self._delayed_states: asyncio.Queue[tuple[float, LavaLampState]] = asyncio.Queue()
        self._latest_accepted_state: LavaLampState | None = None
        self._error_backoff = INITIAL_ERROR_BACKOFF
        self._next_error_log_at = 0.0

    def start(self) -> None:
        if self._task is None or self._task.done():
            self._task = self.hass.async_create_task(self._run(), name="lava_lamp")
        if (
            self.emit_delay_seconds > 0
            and (self._publisher_task is None or self._publisher_task.done())
        ):
            self._publisher_task = self.hass.async_create_task(
                self._publish_delayed_states(),
                name="lava_lamp_delayed_publisher",
            )

    def stop(self) -> None:
        if self._task is not None:
            self._task.cancel()
        if self._publisher_task is not None:
            self._publisher_task.cancel()

    async def _async_update_data(self) -> LavaLampState:
        return await self._fetch_state()

    async def _run(self) -> None:
        while True:
            try:
                await self._stream_sse()
            except asyncio.CancelledError:
                raise
            except SSERejectedError:
                await self._poll_until_sse_retry()
            except (TimeoutError, ClientError, ValueError, json.JSONDecodeError) as err:
                self._log_request_error("SSE connection failed", err)
                self._set_unavailable()
                await self._poll_until_sse_retry()

    async def _stream_sse(self) -> None:
        timeout = ClientTimeout(
            total=None,
            sock_connect=10.0,
            sock_read=HEARTBEAT_TIMEOUT,
        )
        async with self.session.get(self._url("/v1/events"), timeout=timeout) as response:
            if response.status in SSE_REJECTED_STATUSES:
                raise SSERejectedError(f"SSE rejected with HTTP {response.status}")
            response.raise_for_status()

            parser = _SSEEvent()
            while not response.content.at_eof():
                raw_line = await response.content.readline()
                if not raw_line:
                    break
                data = parser.feed(raw_line.decode("utf-8").rstrip("\r\n"))
                if data is None:
                    continue
                self._accept_state(LavaLampState.from_api(json.loads(data)))

    async def _poll_until_sse_retry(self) -> None:
        deadline = self.hass.loop.time() + SSE_RETRY_INTERVAL

        while self.hass.loop.time() < deadline:
            try:
                state = await self._fetch_state()
            except (TimeoutError, ClientError, ValueError, json.JSONDecodeError) as err:
                self._log_request_error("Lava lamp polling failed", err)
                self._set_unavailable()
                await asyncio.sleep(self._error_backoff)
                self._error_backoff = min(self._error_backoff * 2, MAX_ERROR_BACKOFF)
                continue

            self._error_backoff = INITIAL_ERROR_BACKOFF
            self._accept_state(state)
            await asyncio.sleep(_poll_interval_for(state))

    async def _fetch_state(self) -> LavaLampState:
        timeout = ClientTimeout(total=10.0)
        async with self.session.get(self._url("/v1/rgb"), timeout=timeout) as response:
            response.raise_for_status()
            return LavaLampState.from_api(await response.json())

    def _accept_state(self, state: LavaLampState) -> None:
        previous = self._latest_accepted_state
        if previous is not None:
            if state.last_set_unix_ms < previous.last_set_unix_ms:
                return
            if (
                state.last_set_unix_ms == previous.last_set_unix_ms
                and state.rgb == previous.rgb
                and state.live == previous.live
            ):
                return
        self._latest_accepted_state = state
        if self.emit_delay_seconds <= 0:
            self.async_set_updated_data(state)
            return
        self._delayed_states.put_nowait(
            (self.hass.loop.time() + self.emit_delay_seconds, state)
        )

    async def _publish_delayed_states(self) -> None:
        while True:
            release_at, state = await self._delayed_states.get()
            await asyncio.sleep(max(0.0, release_at - self.hass.loop.time()))
            self.async_set_updated_data(state)

    def _set_unavailable(self) -> None:
        if self.data is not None:
            self.async_set_updated_data(None)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _log_request_error(self, message: str, err: Exception) -> None:
        now = self.hass.loop.time()
        if now >= self._next_error_log_at:
            self._next_error_log_at = now + ERROR_LOG_INTERVAL
            LOGGER.warning("%s: %s", message, err)
        else:
            LOGGER.debug("%s: %s", message, err)


def _poll_interval_for(state: LavaLampState) -> float:
    if state.live:
        return FAST_POLL_INTERVAL
    return OFFLINE_POLL_INTERVAL


class _SSEEvent:
    def __init__(self) -> None:
        self._data: list[str] = []

    def feed(self, line: str) -> str | None:
        if line == "":
            if not self._data:
                return None
            data = "\n".join(self._data)
            self._data.clear()
            return data

        if line.startswith(":"):
            return None

        field, _, value = line.partition(":")
        if value.startswith(" "):
            value = value[1:]
        if field == "data":
            self._data.append(value)
        return None
