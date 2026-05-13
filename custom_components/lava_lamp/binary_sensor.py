"""Binary sensor platform for Unofficial Lava Lamp."""

from __future__ import annotations

from homeassistant.components.binary_sensor import BinarySensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LavaLampCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lava lamp binary sensors."""
    coordinator: LavaLampCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([LavaLampLiveBinarySensor(coordinator, entry)])


class LavaLampLiveBinarySensor(
    CoordinatorEntity[LavaLampCoordinator], BinarySensorEntity
):
    """Live state for the lava lamp."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:broadcast"
    _attr_translation_key = "live"

    def __init__(self, coordinator: LavaLampCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_live"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Lava Lamp",
            "manufacturer": "Unofficial Lava Lamp",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def is_on(self) -> bool | None:
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.live
