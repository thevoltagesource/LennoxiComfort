"""
Lennox iComfort API
By Jacob Southard (sandlewoodshire)
Based on the work done by Jarome Avondo (ut666)

Notes: 
  The away setting on the thermostat can only (from what I can find) be set on the 
  thermostat. 

  Currently only supports manual mode (no programs) on the thermosat. 

Issues:

Ideas/Future:
  Support thermostat programs
  Set Away temps (maybe)
  Not sure what state is reported when system is cooling to dehumidify

Change log:

  20180217 - Initial commit. Supports all the features I needed to get Home Assistant controlling/monitoring my thermostat.

"""

import requests

class Lennox_iComfort_API():
    """Representation of the Lennox iComfort thermostat."""
    
    def __init__(self, username, password, system=0, zone=0, units=0):
        """Initialize the interface"""
        self._username = username
        self._credentials = (username, password)
        self._system = system # I only have one system so I default to the first one
        self._zone = zone # I only have one zone so I default to the first one
        self._temp_units = str(units) #0 = F, 1 = C;  I default to F.

        self._service_url = "https://services.myicomfort.com/DBAcessService.svc/";

        self._serial_number = None

        self._heat_to = None
        self._cool_to = None
        self._awaycoolto = None # furture feature
        self._awayheatto = None # future feature
        self._away_mode = None
        self._programmode = None

        self._state = None
        self._state_list = ['Idle', 'Heating', 'Cooling']
        self._program = None  # future feature
        self._program_list = [] # future feature
        self._op_mode = None
        self._fan_mode = None

        self.current_temperature = None
        self.current_humidity = None
        self.op_mode_list = ['Off', 'Heat only', 'Cool only', 'Heat & Cool']
        self.fan_mode_list = ['Auto', 'On', 'Circulate']

        self._get_serial_number()
        self.pull_status()
    
    def _get_serial_number(self):
        # Retrieve serial number for indicated system
        commandURL = self._service_url + "GetSystemsInfo?UserId=" + self._username
        resp = requests.get(commandURL, auth=self._credentials)
        print(resp)
        print(self._system)
        self._serial_number= resp.json()["Systems"][self._system]["Gateway_SN"]

    @property
    def state(self):
        """ Return current operational state """
        return self._state_list[self._state]
    
    @property
    def op_mode(self):
        """ Return current operational mode """
        return self.op_mode_list[self._op_mode]

    @op_mode.setter
    def op_mode(self, value):
        """ Set operational mode """
        self._op_mode = self.op_mode_list.index(value)
        self._push_settings()

    @property
    def fan_mode(self):
        """ Return current fan mode """
        return self.fan_mode_list[self._fan_mode]

    @fan_mode.setter
    def fan_mode(self, value):
        """ Set fan mode """
        self._fan_mode = self.fan_mode_list.index(value)
        self._push_settings()

    @property
    def set_points(self):
        """ Return current temperature set points """
        return (self._heat_to, self._cool_to)

    @set_points.setter
    def set_points(self, value):
        """ Set temperature set points """
        if isinstance(value, tuple):
            if len(value) == 2:
                self._heat_to = min(value)
                self._cool_to = max(value)
            elif self._op_mode == 2:
                self._cool_to = max(value)
            elif self._op_mode == 1:
                self._heat_to = min(value)
        elif isinstance(value, int) or instinstance(value, float):
            """ If we were provided a single value, set temp for current mode """
            if self._op_mode == 2:
                self._cool_to = value
            elif self._op_mode == 1:
                self._heat_to = value
        self._push_settings()

    @property
    def away_mode(self):
        """ Return away mode status """
        return self._away_mode

    @away_mode.setter
    def away_mode(self, value):
        """ Set away mode """
        commandURL = self._service_url + "SetAwayModeNew?gatewaysn=" + self._serial_number + "&awaymode=" + str(value)
        resp = requests.put(commandURL, auth=self._credentials);

    def pull_status(self):
        """ Retrieve current thermosat status/settings """

        commandURL = self._service_url + "GetTStatInfoList?gatewaysn=" + self._serial_number + "&TempUnit=" + self._temp_units
        resp = requests.get(commandURL, auth=self._credentials);
        #print (resp.json())

        #fetch the stats for the requested zone
        statInfo = resp.json()['tStatInfo'][self._zone];

        #Current State
        self._state = int(statInfo['System_Status']);

        #Current Operation Mode
        self._op_mode = int(statInfo['Operation_Mode']);
        
        #Current Fan Mode
        self._fan_mode = int(statInfo['Fan_Mode']);
                
        #Away mode status
        self._away_mode = int(statInfo['Away_Mode']);
        
        #Indoor temperature
        self.current_temperature = float(statInfo['Indoor_Temp']);

        #Indoor humidity
        self.current_humidity = float(statInfo['Indoor_Humidity']);

        #Setpoints
        self._heat_to = float(statInfo['Heat_Set_Point']);
        self._cool_to = float(statInfo['Cool_Set_Point']);
            
        
    def _push_settings(self):
        """ Push settings to thermosat """
        data = {
            'Cool_Set_Point':self._cool_to, 
            'Heat_Set_Point':self._heat_to, 
            'Fan_Mode':self._fan_mode, 
            'Operation_Mode':self._op_mode, 
            'Pref_Temp_Units':self._temp_units, 
            'Zone_Number':self._zone, 
            'GatewaySN':self._serial_number}
        
        commandURL = self._service_url + "SetTStatInfo"
        headers = {'contentType': 'application/x-www-form-urlencoded', 'requestContentType': 'application/json; charset=utf-8'}
        resp = requests.put(commandURL, auth=self._credentials, json=data, headers=headers);
        # print (resp)


