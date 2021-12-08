"""
Lennox iComfort WiFi Climate Component for Home Assisant.

By Jacob Southard (github.com/thevoltagesource)
Based on the work of Jerome Avondo (github.com/ut666)

Tested against Home Assistant Version: 2021.11.3

Notes:
  The away mode set points can only be set on the thermostat.  The code below
  prevents changing set points when in away mode so there are no surprises
  when leaving away mode.

Issues:

Ideas/Future:

Change log:
  202112xx - Map api state = 3 (system waiting) as CURRENT_HVAC_IDLE. Add 
             item system_waiting to extra_device_attributes as (boolean) True
             when state = 3 otherwise False.
  20211206 - Added SUPPORT_AUX_HEAT. Made required changes to integration to 
             handle aux/emergency heat mode. API also required changes so the
             required version was updated (>= v0.5.x).
             also updated to support this mode.
  20210609 - Bug Fix - Changed set_temperature logic to handle the way HomeKit
             updates set points. Changed changed device_state_attributes to
             extras_state_attributes to match climate platform change in 
             HA 2021.4
  20210507 - Update manifest.json file to add required items.
  20200620 - Changed from ClimateDevice to CliemateEntity to support new
             climate standard introduced in HA v0.110.
  20200222 - Bump API version number.
  20191222 - Bug fix - bump API version which addressed a zone selection bug.         
  20191221 - Added support for AirEase thermostats.           
  20190721 - Added ability to select cloud service (Lennox or AirEase).
             Now verifies cloud API connection before adding entity to HA.
             Requires myicomfort API v0.3.0 or higher
  20190720 - Changed code to be HA Climate 1.0 compliant. The climate
             integration was redesigned in Home Assistant 0.96.
  20190505 - Moved requirements to manifest.json. Bumped API requirement to
             myicomfort=0.2.1
  20190314 - Changeed climate.const import to match HA change. Changed layout
             to match new HA 0.88 architecture.
  20190127 - Fixed items flagged by flask8 and pylint
  20190125 - Switched reliance from local api file to PyPI hosted myicomfort
             project. Moved import statement and added REQUIREMENTS variable
             to match HA coding standards.
  20190111 - Cleaned up code.
  20181211 - Changed state() to return item from list of STATE_* constants so
             the state will display in Lovelace. Removed manual entry of
             current humidity in device attributes as 0.83 does this natively
             now.
  20181202 - Updated to work with changes made to API. Added configurable min
             and max temp properties.
  20181129 - Added TEMP_UNITS list and created property for temperature_unit to
             report units used by tstat.
  20181126 - Switched fan and op modes to report/accept HA STATE constants so
             component meets current HA standards. This change fixes
             compactibility with the Lovelace thermostate card. Cleaned up
             notes/documentation.
  20181125 - Cleaned up and simplified code. Using _api properties directly
             instead of copying to other variables.
  20181124 - Changed Away Mode response to fit current standards.
  20180218 - Initial commit. Provides sensor data and allows control of all
             manual modes.

"""

import logging

import voluptuous as vol

import homeassistant.helpers.config_validation as cv
from homeassistant.components.climate import ClimateEntity, PLATFORM_SCHEMA
from homeassistant.components.climate.const import (
    CURRENT_HVAC_COOL,
    CURRENT_HVAC_HEAT,
    CURRENT_HVAC_IDLE,
    HVAC_MODE_OFF,
    HVAC_MODE_HEAT,
    HVAC_MODE_COOL,
    HVAC_MODE_HEAT_COOL,
    PRESET_AWAY,
    PRESET_NONE,
    SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_RANGE,
    SUPPORT_AUX_HEAT,
    SUPPORT_PRESET_MODE,
    SUPPORT_FAN_MODE,
    FAN_ON,
    FAN_AUTO,
    ATTR_TARGET_TEMP_LOW,
    ATTR_TARGET_TEMP_HIGH,
)
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, TEMP_CELSIUS, TEMP_FAHRENHEIT,
    ATTR_TEMPERATURE)

_LOGGER = logging.getLogger(__name__)

# HA doesn't have a 'circulate' mode defined for fan.
FAN_CIRCULATE = 'circulate'

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE |
                 SUPPORT_TARGET_TEMPERATURE_RANGE |
                 SUPPORT_PRESET_MODE |
                 SUPPORT_FAN_MODE |
                 SUPPORT_AUX_HEAT)

FAN_MODES = [
    FAN_AUTO, FAN_ON, FAN_CIRCULATE
]

HVAC_MODES = [
    HVAC_MODE_OFF, HVAC_MODE_HEAT, HVAC_MODE_COOL, HVAC_MODE_HEAT_COOL
]

HVAC_ACTIONS = [
    CURRENT_HVAC_IDLE, CURRENT_HVAC_HEAT, CURRENT_HVAC_COOL
]

TEMP_UNITS = [
    TEMP_FAHRENHEIT, TEMP_CELSIUS
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required('name'): cv.string,
    vol.Optional('system', default=0): cv.positive_int,
    vol.Optional('zone', default=0): cv.positive_int,
    vol.Optional('min_temp'): vol.Coerce(float),
    vol.Optional('max_temp'): vol.Coerce(float),
    vol.Optional('cloud_svc', default='lennox'): cv.string
})


def setup_platform(hass, config, add_entities, discovery_info=None):
    """Set up the climate platform."""
    from myicomfort.api import Tstat

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    system = config.get('system')
    zone = config.get('zone')
    name = config.get('name')
    min_temp = config.get('min_temp')
    max_temp = config.get('max_temp')
    service = config.get('cloud_svc')

    tstat = Tstat(username, password, system, zone, service)
    climate = [LennoxClimate(name, min_temp, max_temp, tstat)]

    if tstat.connected:
        add_entities(climate, True)
    else:
        _LOGGER.error('Failed to connect to thermostat cloud API.')


class LennoxClimate(ClimateEntity):
    """Class for Lennox iComfort WiFi thermostat."""

    def __init__(self, name, min_temp, max_temp, api):
        """Initialize the climate device."""
        self._name = name
        self._api = api
        self._min_temp = min_temp
        self._max_temp = max_temp

    def update(self):
        """Update data from the thermostat API."""
        self._api.pull_status()

    @property
    def extra_state_attributes(self):
        """Return device specific state attributes."""
        data = {}
        data["system_waiting"] = True if self._api.state == 3 else False
        return data

    @property
    def name(self):
        """Return the name of the climate device."""
        return self._name

    @property
    def supported_features(self):
        """Return the list of supported features."""
        return SUPPORT_FLAGS

    @property
    def temperature_unit(self):
        """Return the unit of measurement."""
        return TEMP_UNITS[self._api.temperature_units]

    @property
    def min_temp(self):
        """Return the minimum temperature."""
        if self._min_temp is not None:
            return self._min_temp
        return super().min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._max_temp is not None:
            return self._max_temp
        return super().max_temp

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self._api.op_mode == 1 or self._api.op_mode == 4:
            return min(self._api.set_points)
        if self._api.op_mode == 2:
            return max(self._api.set_points)
        return None

    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._api.current_temperature

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        if self._api.op_mode == 3:
            return max(self._api.set_points)
        return None

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        if self._api.op_mode == 3:
            return min(self._api.set_points)
        return None

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._api.current_humidity

    @property
    def hvac_mode(self):
        """Return the current hvac operation mode."""
        if self._api.op_mode == 4:
            return HVAC_MODE_HEAT
        return HVAC_MODES[self._api.op_mode]

    @property
    def hvac_modes(self):
        """Return the list of available hvac operation modes."""
        return HVAC_MODES

    @property
    def hvac_action(self):
        """Return the current hvac state/action."""
        if self._api.state == 3:
            return CURRENT_HVAC_IDLE
        return HVAC_ACTIONS[self._api.state]

    @property
    def preset_mode(self):
        """Return the current preset mode."""
        if self._api.away_mode == 1:
            return PRESET_AWAY
        return None

    @property
    def preset_modes(self):
        """Return a list of available preset modes."""
        return [PRESET_NONE, PRESET_AWAY]

    @property
    def is_away_mode_on(self):
        """Return the current away mode status."""
        return self._api.away_mode

    @property
    def is_aux_heat(self):
        """Return the current away mode status."""
        if self._api.op_mode == 4:
            return True
        return False

    @property
    def fan_mode(self):
        """Return the current fan mode."""
        return FAN_MODES[self._api.fan_mode]

    @property
    def fan_modes(self):
        """Return the list of available fan modes."""
        return FAN_MODES

    def set_temperature(self, **kwargs):
        """Set new target temperature. API expects a tuple."""
        if not self._api.away_mode:
            if ((kwargs.get(ATTR_TEMPERATURE) is not None) and (
                self._api.op_mode != 3)):
                self._api.set_points = (kwargs.get(ATTR_TEMPERATURE), )
            else:
                self._api.set_points = (kwargs.get(ATTR_TARGET_TEMP_LOW),
                                        kwargs.get(ATTR_TARGET_TEMP_HIGH))

    def set_fan_mode(self, fan_mode):
        """Set new fan mode."""
        if not self._api.away_mode:
            self._api.fan_mode = FAN_MODES.index(fan_mode)

    def set_hvac_mode(self, hvac_mode):
        """Set new hvac operation mode."""
        if not self._api.away_mode:
            self._api.op_mode = HVAC_MODES.index(hvac_mode)

    def set_preset_mode(self, preset_mode):
        """Set new preset mode."""
        if preset_mode == PRESET_AWAY:
            self._turn_away_mode_on()
        else:
            self._turn_away_mode_off()

    def _turn_away_mode_on(self):
        """Turn away mode on."""
        self._api.away_mode = 1

    def _turn_away_mode_off(self):
        """Turn away mode off."""
        self._api.away_mode = 0

    def turn_aux_heat_on(self):
        """Turn auxiliary heater on."""
        self._api.op_mode = 4

    def turn_aux_heat_off(self):
        """Turn auxiliary heater off."""
        self.set_hvac_mode(HVAC_MODE_HEAT)

