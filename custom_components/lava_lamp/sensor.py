"""Sensor platform for Unofficial Lava Lamp."""

from __future__ import annotations

from dataclasses import dataclass
from collections.abc import Callable
from typing import Final

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import LavaLampCoordinator
from .models import LavaLampState


@dataclass(frozen=True, kw_only=True)
class LavaLampSensorDescription(SensorEntityDescription):
    value_fn: Callable[[LavaLampState], int]


SENSORS: Final = (
    LavaLampSensorDescription(
        key="red",
        translation_key="red",
        icon="mdi:palette",
        value_fn=lambda state: state.red,
    ),
    LavaLampSensorDescription(
        key="green",
        translation_key="green",
        icon="mdi:palette",
        value_fn=lambda state: state.green,
    ),
    LavaLampSensorDescription(
        key="blue",
        translation_key="blue",
        icon="mdi:palette",
        value_fn=lambda state: state.blue,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up lava lamp RGB sensors."""

    coordinator: LavaLampCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [LavaLampSensor(coordinator, entry, description) for description in SENSORS]
    )


class LavaLampSensor(CoordinatorEntity[LavaLampCoordinator], SensorEntity):
    """RGB channel sensor for the lava lamp."""

    _attr_has_entity_name = True

    def __init__(
        self,
        coordinator: LavaLampCoordinator,
        entry: ConfigEntry,
        description: LavaLampSensorDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Lava Lamp",
            "manufacturer": "Unofficial Lava Lamp",
        }

    @property
    def available(self) -> bool:
        return self.coordinator.data is not None

    @property
    def native_value(self) -> int | None:
        if self.coordinator.data is None:
            return None
        return self.entity_description.value_fn(self.coordinator.data)
