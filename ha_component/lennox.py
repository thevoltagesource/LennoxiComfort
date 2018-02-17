"""
Lennox iComfort Component for Home Assisant
By Jacob Southard (sandlewoodshire)
Based on the work done by Jarome Avondo (ut666)

Home Assistant Supported Version: 0.63.2

Notes:
  The away setting on the thermostat can only (from what I can find) be set on the 
  thermostat.  I have code in here to prevent settings from being adjusted when in 
  away mode so there are no surprises when leaving away mode.

  Currently only supports manual mode (no programs) on the thermosat. 

Issues:
  Fan mode on more-info card not displayed properly due to polymer bug
  https://github.com/home-assistant/home-assistant-polymer/pull/849

Ideas/Future:
  For more visibility/control (due to away mode behaviour)
    Add attributes for away settings
    Add attributes for non-away settings
  Support thermostat programs

Change log:
  20180218 - Initial commit. Provides sensor data and allows control of all moanual modes.

"""

import logging
import voluptuous as vol

from homeassistant.components.sensor import PLATFORM_SCHEMA
from homeassistant.helpers.entity import Entity
import homeassistant.helpers.config_validation as cv

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

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required(CONF_USERNAME): cv.string,
    vol.Required(CONF_PASSWORD): cv.string,
    vol.Required('name'): cv.string,
    vol.Optional('system', default=0): vol.Coerce(int),
    vol.Optional('zone', default=0): vol.Coerce(int),
})

def setup_platform(hass, config, add_devices, discovery_info=None):
        """Setup the platform."""
        username = config.get(CONF_USERNAME)
        password = config.get(CONF_PASSWORD)
        system = config.get('system')
        zone = config.get('zone')
        name = config.get('name')

        """Create the climate device"""
        climate = [LennoxClimate(name, Lennox_iComfort_API(username, password, system, zone))]
        add_devices(climate, True)

class LennoxClimate(ClimateDevice):

    def __init__(self, name, api):
        """Initialize the climate device."""
        self._name = name
        self._api = api
        self._unit_of_measurement = TEMP_FAHRENHEIT;

        self._current_state = self._api.state
        self._current_temperature = self._api.current_temperature
        self._current_humidity = self._api.current_humidity
        self._current_fan_mode = self._api.fan_mode
        self._current_operation_mode = self._api.op_mode
       
        self._target_temperature_high = max(self._api.set_points)
        self._target_temperature_low = min(self._api.set_points)

        self._program_list = self._api._program_list
        self._fan_list = self._api.fan_mode_list      
        self._operation_list = self._api.op_mode_list

        if self._api._away_mode == 1:
            self._away = 'on'
        else:
            self._away = 'off'
        

    def update(self):
        """Get the latest data from the thermostat API."""
        self._api.pull_status()
        
        """set our sensor values"""
        self._current_temperature = self._api.current_temperature
        self._current_humidity = self._api.current_humidity
        self._target_temperature_high = max(self._api.set_points)
        self._target_temperature_low = min(self._api.set_points)
        self._current_operation_mode = self._api.op_mode                
        self._current_fan_mode = self._api.fan_mode
        self._current_state = self._api.state

        if self._api.away_mode == 1:
            self._away = 'on'
        else: 
            self._away = 'off'
            
    @property
    def device_state_attributes(self):
        """Return device specific state attributes."""
        return {
        # Since we don't support setting humidity, we present current humidity as an attribute.
        "current_humidity": self._current_humidity,
        # Away mode was not always read properly, added attribute to make sure it is visible.
        "away_mode": self._away
        }
        
    @property
    def state(self):
        """ Return current operational state """
        return self._current_state
            
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
        return self._unit_of_measurement
        
    @property
    def target_temperature(self):
        """Return the temperature we try to reach."""
        if self.current_operation == 'Heat only':
            return self._target_temperature_low
        elif self.current_operation == 'Cool only':
            return self._target_temperature_high
        else:
            return None
    @property
    def current_temperature(self):
        """Return the current temperature."""
        return self._current_temperature

    @property
    def target_temperature_high(self):
        """Return the highbound target temperature we try to reach."""
        if self.current_operation == 'Heat & Cool':
            return self._target_temperature_high
        else:
            return None

    @property
    def target_temperature_low(self):
        """Return the lowbound target temperature we try to reach."""
        if self.current_operation == 'Heat & Cool':
            return self._target_temperature_low
        else:
            return None

    @property
    def current_humidity(self):
        """Return the current humidity."""
        return self._current_humidity

    @property
    def current_operation(self):
        return self._current_operation_mode
        
    @property
    def operation_list(self):
        """Return the list of available operation modes."""
        return self._operation_list

    @property
    def is_away_mode_on(self):
        """Return if away mode is on."""
        return self._away

    @property
    def current_fan_mode(self):
        return self._current_fan_mode
        
    @property
    def fan_list(self):
        """Return the list of available fan modes."""
        return self._fan_list
        
    def set_temperature(self, **kwargs):
        """Set new target temperature. API expects a tuple with one or two temperatures"""
        if self._away == 'off':
            if kwargs.get(ATTR_TEMPERATURE) is not None:
                self._api.set_points = (kwargs.get(ATTR_TEMPERATURE), )
            else:
                self._api.set_points = (kwargs.get(ATTR_TARGET_TEMP_LOW), kwargs.get(ATTR_TARGET_TEMP_HIGH))

    def set_fan_mode(self, fan):
        """Set new fan mode."""
        if self._away == 'off':
            self._api.fan_mode = fan

    def set_operation_mode(self, operation_mode):
        """Set new operation mode."""
        if self._away == 'off':
            self._api.op_mode = operation_mode
                    
    def turn_away_mode_on(self):
        """Turn away mode on."""
        self._api.away_mode = 1

    def turn_away_mode_off(self):
        """Turn away mode off."""
        self._api.away_mode = 0


