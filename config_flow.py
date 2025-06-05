from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers import selector
from .const import DOMAIN

class HalachicContextConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Config flow for Halachic Context."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        if user_input is not None:
            # למנוע התקנה כפולה
            existing_entries = self._async_current_entries()
            if existing_entries:
                return self.async_abort(reason="single_instance_allowed")
            return self.async_create_entry(title="Halachic Context", data=user_input)

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({}),
            description_placeholders={},
        )

    @staticmethod
    @callback
    def async_get_options_flow(entry):
        return HalachicContextOptionsFlowHandler(entry)


class HalachicContextOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options."""

    def __init__(self, entry):
        self.entry = entry

    async def async_step_init(self, user_input=None):
        return self.async_show_form(step_id="init", data_schema=vol.Schema({}))
