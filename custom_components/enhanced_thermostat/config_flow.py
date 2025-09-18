"""Config flow for Enhanced Thermostat integration."""
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.helpers.selector import (
    EntitySelector,
    EntitySelectorConfig,
    TextSelector,
    TextSelectorConfig,
    TextSelectorType,
)

from .const import DOMAIN


class EnhancedThermostatConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Enhanced Thermostat."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}

        if user_input is not None:
            await self.async_set_unique_id(user_input["thermostat_entity_id"])
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Enhanced Thermostat", data=user_input)

        schema = vol.Schema(
            {
                vol.Required("thermostat_entity_id"): EntitySelector(
                    EntitySelectorConfig(domain="climate"),
                ),
                vol.Optional("safety_min_temp"): vol.Coerce(float),
                vol.Optional("safety_max_temp"): vol.Coerce(float),
                vol.Optional("schedule"): TextSelector(
                    TextSelectorConfig(type=TextSelectorType.TEXT, multiline=True),
                ),
            }
        )

        return self.async_show_form(
            step_id="user", data_schema=schema, errors=errors
        )
