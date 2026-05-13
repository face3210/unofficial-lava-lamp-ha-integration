"""Config flow for the Unofficial Lava Lamp integration."""

from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import (
    CONF_EMIT_DELAY_SECONDS,
    CONF_URL,
    DEFAULT_BASE_URL,
    DEFAULT_EMIT_DELAY_SECONDS,
    DOMAIN,
)


def _validate_url(value: str) -> str:
    value = str(value).strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise vol.Invalid("invalid_url")
    return value


def _validate_emit_delay_seconds(value: float) -> float:
    try:
        delay = float(value)
    except (TypeError, ValueError) as err:
        raise vol.Invalid("invalid_emit_delay_seconds") from err
    if delay < 0:
        raise vol.Invalid("invalid_emit_delay_seconds")
    return delay


def _config_schema(url: str, emit_delay_seconds: float) -> vol.Schema:
    return vol.Schema(
        {
            vol.Required(CONF_URL, default=url): str,
            vol.Required(
                CONF_EMIT_DELAY_SECONDS,
                default=emit_delay_seconds,
            ): vol.Coerce(float),
        }
    )


class LavaLampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unofficial Lava Lamp."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> config_entries.OptionsFlow:
        return LavaLampOptionsFlow(config_entry)

    async def async_step_user(
        self, user_input: dict[str, str | float] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            try:
                url = _validate_url(user_input[CONF_URL])
                emit_delay_seconds = _validate_emit_delay_seconds(
                    user_input[CONF_EMIT_DELAY_SECONDS]
                )
            except vol.Invalid:
                errors["base"] = "invalid_input"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Unofficial Lava Lamp",
                    data={
                        CONF_URL: url,
                        CONF_EMIT_DELAY_SECONDS: emit_delay_seconds,
                    },
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_config_schema(DEFAULT_BASE_URL, DEFAULT_EMIT_DELAY_SECONDS),
            errors=errors,
        )


class LavaLampOptionsFlow(config_entries.OptionsFlow):
    """Handle options for Unofficial Lava Lamp."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        self._config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, str | float] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if user_input is not None:
            try:
                url = _validate_url(user_input[CONF_URL])
                emit_delay_seconds = _validate_emit_delay_seconds(
                    user_input[CONF_EMIT_DELAY_SECONDS]
                )
            except vol.Invalid:
                errors["base"] = "invalid_input"
            else:
                return self.async_create_entry(
                    title="",
                    data={
                        CONF_URL: url,
                        CONF_EMIT_DELAY_SECONDS: emit_delay_seconds,
                    },
                )

        url = self._config_entry.options.get(
            CONF_URL,
            self._config_entry.data.get(CONF_URL, DEFAULT_BASE_URL),
        )
        emit_delay_seconds = self._config_entry.options.get(
            CONF_EMIT_DELAY_SECONDS,
            self._config_entry.data.get(
                CONF_EMIT_DELAY_SECONDS,
                DEFAULT_EMIT_DELAY_SECONDS,
            ),
        )
        return self.async_show_form(
            step_id="init",
            data_schema=_config_schema(url, emit_delay_seconds),
            errors=errors,
        )
