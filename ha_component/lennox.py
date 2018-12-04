"""
Lennox iComfort WiFi Climate Component for Home Assisant
By Jacob Southard (github.com/sandlewoodshire)
Based on the work of Jarome Avondo (github.com/ut666)

Tested against Home Assistant Version: 0.81.2

Notes:
  The away mode set points can only be set on the thermostat.  The code below prevents changing set points 
  when in away mode so there are no surprises when leaving away mode.

  Fan mode now uses STATE variables but there is no circuilate state. I added a text entry to FAN_MODES to account for this.
  Fan mode now uses STATE variables but frontend doesn't auto capitalize fan mode like it does for op mode.

  Currently this only supports manual mode (no programs) on the thermosat. I have not pursued creating this since I want HA managing
  the thermostat behavior and not the thermostat itself.

Issues:
  Need to make unit of measure configurable instead of hard coded.

Ideas/Future:
  Support thermostat programs

Change log:
  20181202 - Updated to work with changes made to API.  Added configurable min and max temp properties.
  20181129 - Added TEMP_UNITS list and created property for temperature_unit to report units used by tstat.  
  20181126 - Switched fan and op modes to report/accept HA STATE variables so component meets current HA standards.
             This change fixes compactibility with the Lovelace thermostate card. Cleaned up notes/documentation.
  20181125 - Cleaned up and simplified code. Using _api properties directly instead of copying to other variables.
  20181124 - Changed AwayMode responseto fit current standards.
  20180218 - Initial commit. Provides sensor data and allows control of all manual modes.

"""

import logging
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

from homeassistant.util.temperature import convert as convert_temperature

from homeassistant.components.climate import (
    ATTR_TARGET_TEMP_HIGH, ATTR_TARGET_TEMP_LOW, DOMAIN,
    ClimateDevice, PLATFORM_SCHEMA, STATE_AUTO,
    STATE_COOL, STATE_HEAT, SUPPORT_TARGET_TEMPERATURE,
    SUPPORT_TARGET_TEMPERATURE_HIGH, SUPPORT_TARGET_TEMPERATURE_LOW,
    SUPPORT_OPERATION_MODE, SUPPORT_AWAY_MODE, SUPPORT_FAN_MODE)
from homeassistant.const import (
    CONF_USERNAME, CONF_PASSWORD, TEMP_CELSIUS, TEMP_FAHRENHEIT,
    STATE_ON, STATE_OFF, STATE_UNKNOWN,
    ATTR_TEMPERATURE, EVENT_HOMEASSISTANT_START)

from custom_components.climate.lennox_api import Lennox_iComfort_API

_LOGGER = logging.getLogger(__name__)

SUPPORT_FLAGS = (SUPPORT_TARGET_TEMPERATURE_HIGH | SUPPORT_TARGET_TEMPERATURE |
                 SUPPORT_TARGET_TEMPERATURE_LOW | SUPPORT_OPERATION_MODE |
                 SUPPORT_AWAY_MODE | SUPPORT_FAN_MODE)

# List ordered to match API values.
OP_MODES = [
    STATE_OFF, STATE_HEAT, STATE_COOL, STATE_AUTO
]

# List ordered to match API values. HA doesn't have a 'circulate' state defined.
FAN_MODES = [
    STATE_AUTO, STATE_ON, 'circulate'
]

# List ordered to match API values.
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
        username = config.get(CONF_USERNAME)
        password = config.get(CONF_PASSWORD)
        system = config.get('system')
        zone = config.get('zone')
        name = config.get('name')
        min_temp = config.get('min_temp')
        max_temp = config.get('max_temp')

        """Create the climate device"""
        climate = [LennoxClimate(name, min_temp, max_temp, Lennox_iComfort_API(username, password, system, zone))]
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
        # Since we don't support setting humidity, we present the current humidity as an attribute.
        'current_humidity': self._api.current_humidity
        }
        
    @property
    def state(self):
        """Return the current operational state."""
        return self._api.state_list[self._api.state]
            
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
        """Return the current humidity. Currently unused as HA only uses this if SUPPORT_TARGET_HUMIDITY is a supported feature"""
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
        """Set new target temperature. API expects a tuple with one or two temperatures."""
        if not self._api.away_mode:
            if kwargs.get(ATTR_TEMPERATURE) is not None:
                self._api.set_points = (kwargs.get(ATTR_TEMPERATURE), )
            else:
                self._api.set_points = (kwargs.get(ATTR_TARGET_TEMP_LOW), kwargs.get(ATTR_TARGET_TEMP_HIGH))

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


