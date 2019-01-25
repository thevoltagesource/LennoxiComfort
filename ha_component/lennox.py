"""
Lennox iComfort WiFi Climate Component for Home Assisant
By Jacob Southard (github.com/thevoltagesource)
Based on the work of Jerome Avondo (github.com/ut666)

Tested against Home Assistant Version: 0.85.0

Notes:
  The away mode set points can only be set on the thermostat.  The code below
  prevents changing set points when in away mode so there are no surprises
  when leaving away mode.

  Since HA changed to using standardized STATE_* constants for device state and
  operation mode, I change fan mode to also use those constants. Hwever, there
  is no STATE_CIRCULATE, so I define one, and the frontend doesn't auto 
  capitalize fan mode like it does for op mode so this doesn't look consistant.

Issues:

Ideas/Future:

Change log:
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

from homeassistant.components.climate import (
    ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW,
    ClimateDevice, PLATFORM_SCHEMA, STATE_AUTO,
    STATE_COOL, STATE_HEAT, SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_HIGH, SUPPORT_TARGET_TEMPERATURE_LOW,
    SUPPORT_OPERATION_MODE, SUPPORT_AWAY_MODE, SUPPORT_FAN_MODE)
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, TEMP_CELSIUS, TEMP_FAHRENHEIT,
    STATE_ON, STATE_OFF, STATE_IDLE, ATTR_TEMPERATURE)

REQUIREMENTS = ['myicomfort==0.2.0']

_LOGGER = logging.getLogger(__name__)

# HA doesn't have a 'circulate' state defined.
STATE_CIRCULATE = 'circulate'

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE |
                 SUPPORT_TARGET_TEMPERATURE_HIGH | 
                 SUPPORT_TARGET_TEMPERATURE_LOW |
                 SUPPORT_OPERATION_MODE |
                 SUPPORT_AWAY_MODE |
                 SUPPORT_FAN_MODE)

FAN_MODES = [
    STATE_AUTO, STATE_ON, STATE_CIRCULATE
]

OP_MODES = [
    STATE_OFF, STATE_HEAT, STATE_COOL, STATE_AUTO
]

SYSTEM_STATES = [
    STATE_IDLE, STATE_HEAT, STATE_COOL
]

TEMP_UNITS = [
	TEMP_FAHRENHEIT, TEMP_CELSIUS
]

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required('name'): cv.string,
    vol.Optional('system', default=0): vol.Coerce(int),
    vol.Optional('zone', default=0): vol.Coerce(int),
    vol.Optional('min_temp'): vol.Coerce(float),
    vol.Optional('max_temp'): vol.Coerce(float),
})

def setup_platform(hass, config, add_devices, discovery_info=None):
    """Setup the platform."""
    from myicomfort.api import Tstat

    username = config.get(CONF_USERNAME)
    password = config.get(CONF_PASSWORD)
    system = config.get('system')
    zone = config.get('zone')
    name = config.get('name')
    min_temp = config.get('min_temp')
    max_temp = config.get('max_temp')

    climate = [LennoxClimate(name, min_temp, max_temp,
               Tstat(username, password, system, zone))]

    add_devices(climate, True)

class LennoxClimate(ClimateDevice):

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
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return {
        }
        
    @property
    def state(self):
        """Return the current operational state."""
        return SYSTEM_STATES[self._api.state]
            
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
        if self._min_temp:
        	return self._min_temp
        return super().min_temp

    @property
    def max_temp(self):
        """Return the maximum temperature."""
        if self._max_temp:
        	return self._max_temp
        return super().max_temp

    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self._api.op_mode == 1:
            return min(self._api.set_points)
        elif self._api.op_mode == 2:
            return max(self._api.set_points)
        else:
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
        else:
            return None

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        if self._api.op_mode == 3:
            return min(self._api.set_points)
        else:
            return None

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._api.current_humidity

    @property
    def current_operation(self):
        """Return the current operation mode."""
        return OP_MODES[self._api.op_mode]
        
    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return OP_MODES

    @property
    def is_away_mode_on(self):
        """Return the current away mode status."""
        return self._api.away_mode

    @property
    def current_fan_mode(self):
        """Return the current fan mode."""
        return FAN_MODES[self._api.fan_mode]
        
    @property
    def fan_list(self):
        """Return the list of available fan modes."""
        return FAN_MODES
        
    def set_temperature(self, **kwargs):
        """Set new target temperature. API expects a tuple."""
        if not self._api.away_mode:
            if kwargs.get(ATTR_TEMPERATURE) is not None:
                self._api.set_points = (kwargs.get(ATTR_TEMPERATURE), )
            else:
                self._api.set_points = (kwargs.get(ATTR_TARGET_TEMP_LOW),
                                        kwargs.get(ATTR_TARGET_TEMP_HIGH))

    def set_fan_mode(self, fan):
        """Set new fan mode."""
        if not self._api.away_mode:
            self._api.fan_mode = FAN_MODES.index(fan)

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        if not self._api.away_mode:
            self._api.op_mode = OP_MODES.index(operation_mode)
                    
    def turn_away_mode_on(self):
        """Turn away mode on."""
        self._api.away_mode = 1

    def turn_away_mode_off(self):
        """Turn away mode off."""
        self._api.away_mode = 0


