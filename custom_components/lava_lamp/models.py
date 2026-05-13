"""Data models for the Unofficial Lava Lamp integration."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class LavaLampState:
    """Current lava lamp state from the API."""

    rgb: tuple[int, int, int]
    hex: str
    last_set_unix_ms: int
    live: bool

    @property
    def red(self) -> int:
        return self.rgb[0]

    @property
    def green(self) -> int:
        return self.rgb[1]

    @property
    def blue(self) -> int:
        return self.rgb[2]

    @property
    def rgb_list(self) -> list[int]:
        return list(self.rgb)

    @classmethod
    def from_api(cls, data: dict[str, Any]) -> "LavaLampState":
        rgb = data.get("rgb")
        if not isinstance(rgb, list | tuple) or len(rgb) != 3:
            raise ValueError("rgb must be a three-item list")

        rgb_tuple = tuple(int(channel) for channel in rgb)
        if any(channel < 0 or channel > 255 for channel in rgb_tuple):
            raise ValueError("rgb channels must be between 0 and 255")

        return cls(
            rgb=rgb_tuple,  # type: ignore[arg-type]
            hex=str(data["hex"]),
            last_set_unix_ms=int(data["lastSetUnixMs"]),
            live=bool(data["live"]),
        )
