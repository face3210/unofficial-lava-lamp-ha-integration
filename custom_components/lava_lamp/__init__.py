"""Unofficial Lava Lamp integration."""

from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant

from .const import (
    CONF_EMIT_DELAY_SECONDS,
    CONF_URL,
    DEFAULT_EMIT_DELAY_SECONDS,
    DOMAIN,
)
from .coordinator import LavaLampCoordinator

PLATFORMS = [Platform.BINARY_SENSOR, Platform.SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Unofficial Lava Lamp from a config entry."""

    coordinator = LavaLampCoordinator(
        hass,
        entry.options.get(CONF_URL, entry.data[CONF_URL]),
        entry.options.get(
            CONF_EMIT_DELAY_SECONDS,
            entry.data.get(CONF_EMIT_DELAY_SECONDS, DEFAULT_EMIT_DELAY_SECONDS),
        ),
    )
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    coordinator.start()
    entry.async_on_unload(coordinator.stop)
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""

    coordinator: LavaLampCoordinator = hass.data[DOMAIN][entry.entry_id]
    coordinator.stop()

    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok


async def _async_update_listener(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload the integration when options change."""

    await hass.config_entries.async_reload(entry.entry_id)
