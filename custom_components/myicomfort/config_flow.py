"""Config flow for the Lennox iComfort integration."""

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_NAME, CONF_PASSWORD, CONF_USERNAME
import homeassistant.helpers.config_validation as cv

from . import DOMAIN


CONF_SYSTEM = "system"
CONF_ZONE = "zone"
CONF_MIN_TEMP = "min_temp"
CONF_MAX_TEMP = "max_temp"
CONF_CLOUD_SERVICE = "cloud_svc"


class MyIcomfortConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle one Lennox iComfort system/zone as one hub."""

    VERSION = 4

    async def async_step_user(self, user_input=None):
        """Handle initial setup."""
        errors = {}
        if user_input is not None:
            await self.async_set_unique_id(self._unique_id(user_input))
            self._abort_if_unique_id_configured()
            try:
                await self._test_connection(user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(
                    title=user_input[CONF_NAME], data=user_input
                )

        return self.async_show_form(
            step_id="user",
            data_schema=_schema(),
            errors=errors,
        )

    async def async_step_import(self, import_data):
        """Import one legacy YAML climate entry as one hub."""
        data = {
            key: value for key, value in import_data.items() if key != "platform"
        }
        data.setdefault(CONF_SYSTEM, 0)
        data.setdefault(CONF_ZONE, 0)
        data.setdefault(CONF_CLOUD_SERVICE, "lennox")
        await self.async_set_unique_id(self._unique_id(data))
        self._abort_if_unique_id_configured()
        return self.async_create_entry(title=data[CONF_NAME], data=data)

    @staticmethod
    def _unique_id(data):
        """Return a unique ID for one account, system, and zone."""
        return ":".join(
            [
                data[CONF_USERNAME].lower(),
                data.get(CONF_CLOUD_SERVICE, "lennox").lower(),
                str(data.get(CONF_SYSTEM, 0)),
                str(data.get(CONF_ZONE, 0)),
            ]
        )

    async def _test_connection(self, data):
        """Verify the selected system and zone can connect."""
        from myicomfort.api import Tstat

        thermostat = await self.hass.async_add_executor_job(
            Tstat,
            data[CONF_USERNAME],
            data[CONF_PASSWORD],
            data.get(CONF_SYSTEM, 0),
            data.get(CONF_ZONE, 0),
            data.get(CONF_CLOUD_SERVICE, "lennox"),
        )
        if not thermostat.connected:
            raise CannotConnect

    @staticmethod
    def async_get_options_flow(config_entry):
        """Return the options flow for an existing hub."""
        return MyIcomfortOptionsFlow()


class MyIcomfortOptionsFlow(config_entries.OptionsFlow):
    """Edit one hub's account and system/zone settings."""

    async def async_step_init(self, user_input=None):
        """Edit the hub settings."""
        current = self.config_entry.data
        errors = {}
        if user_input is not None:
            data = {**current, **user_input}
            try:
                await self.hass.async_add_executor_job(
                    _test_connection,
                    data,
                )
            except CannotConnect:
                errors["base"] = "cannot_connect"
            else:
                return self.async_create_entry(title="", data=data)

        return self.async_show_form(
            step_id="init",
            data_schema=_schema(current),
            errors=errors,
        )


def _schema(current=None):
    """Build the hub configuration schema."""
    current = current or {}
    schema = {
        vol.Required(CONF_NAME, default=current.get(CONF_NAME, "")): cv.string,
        vol.Required(
            CONF_USERNAME, default=current.get(CONF_USERNAME, "")
        ): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Required(CONF_SYSTEM, default=current.get(CONF_SYSTEM, 0)): cv.positive_int,
        vol.Required(CONF_ZONE, default=current.get(CONF_ZONE, 0)): cv.positive_int,
        vol.Required(
            CONF_CLOUD_SERVICE, default=current.get(CONF_CLOUD_SERVICE, "lennox")
        ): cv.string,
    }
    for key in (CONF_MIN_TEMP, CONF_MAX_TEMP):
        if current.get(key) is None:
            schema[vol.Optional(key)] = vol.Coerce(float)
        else:
            schema[vol.Optional(key, default=current[key])] = vol.Coerce(float)
    return vol.Schema(schema)


def _test_connection(data):
    """Verify the selected system and zone can connect."""
    from myicomfort.api import Tstat

    thermostat = Tstat(
        data[CONF_USERNAME],
        data[CONF_PASSWORD],
        data.get(CONF_SYSTEM, 0),
        data.get(CONF_ZONE, 0),
        data.get(CONF_CLOUD_SERVICE, "lennox"),
    )
    if not thermostat.connected:
        raise CannotConnect


class CannotConnect(Exception):
    """Unable to connect to the thermostat cloud service."""
