"""Config flow for the Unofficial Lava Lamp integration."""

from __future__ import annotations

from urllib.parse import urlparse

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResult

from .const import CONF_URL, DEFAULT_BASE_URL, DOMAIN


def _validate_url(value: str) -> str:
    value = value.strip().rstrip("/")
    parsed = urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        raise vol.Invalid("invalid_url")
    return value


class LavaLampConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Unofficial Lava Lamp."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, str] | None = None
    ) -> FlowResult:
        errors: dict[str, str] = {}

        if self._async_current_entries():
            return self.async_abort(reason="already_configured")

        if user_input is not None:
            try:
                url = _validate_url(user_input[CONF_URL])
            except vol.Invalid:
                errors[CONF_URL] = "invalid_url"
            else:
                await self.async_set_unique_id(DOMAIN)
                self._abort_if_unique_id_configured()
                return self.async_create_entry(
                    title="Unofficial Lava Lamp",
                    data={CONF_URL: url},
                )

        schema = vol.Schema({vol.Required(CONF_URL, default=DEFAULT_BASE_URL): str})
        return self.async_show_form(
            step_id="user",
            data_schema=schema,
            errors=errors,
        )
