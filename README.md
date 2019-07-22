# Lennox iComfort WiFi Component
This code set is my custom component for Home Assistant to integrate with a Lennox iComfort WiFi thermostat. This code only works with the iComfort WiFi and not the iComfort S30 or E30.  To help with the distiction and avoid any head banging, I am renaming the component from lennox to myicomfort. To use this code you must have previously created a myicomfort account and connected your iComfort WiFi thermostat to your account. 

Support for AirEase thermostats linked to mycomfortsync.com has been added to the backend API. As with it's Lennox cousin, you must have previously created a mycomfortsync account and connected your thermostat. The integration has been updated to let you select which cloud service is used by your thermostat. Requires HA 0.96 or newer.

When configuring this integration please make sure to follow the directions for your version of Home Assistant.  There have been a couple of major HA changes that has resulted in version specific code/config for this integration.

The API code used to interface with myicomfort.com (and mycomfortsync.com) has been published to PyPI and HA will install the appropriate version on startup the first time the component is loaded.  You no longer need to manually copy the API code to your installation.  If you previously copied lennox_api.py to your installation it is safe to delete this file now.

### Home Assistant 0.96 and newer
Copy the 'myicomfort' folder and contents to &lt;config directory&gt;/custom_components/ and add the following to your configuration.yaml file:
```yaml
climate:
  - platform: myicomfort
    name: Upstairs
    username: !secret cloudapi_username
    password: !secret cloudapi_password
    system: 0 (optional, default = 0)
    zone: 0 (optional, default = 0)
    min_temp: 55 (optional, default = 45)
    max_temp: 90 (optional, default = 95)
    cloud_svc: airease (optional, default = 'lennox', other valid option is 'airease')
```
Platform has to be 'myicomfort' but everything else is your's to customize. Don't include the parentheses in your config.  Those are just my way of putting some inline notes in this example.

### Home Assistant 0.88 to 0.95
Copy the 'myicomfort-old' folder and contents to &lt;config directory&gt;/custom_components/, rename the folder to 'myicomfort', and add the following to your configuration.yaml file:
```yaml
climate:
  - platform: myicomfort
    name: lennox
    username: !secret icomfort_username
    password: !secret icomfort_password
    system: 0 (optional, default = 0)
    zone: 0 (optional, default = 0)
    min_temp: 55 (optional, default = 45)
    max_temp: 90 (optional, default = 95)
```
Platform has to be 'myicomfort' but everything else is your's to customize. This version does not support the AirEase thermostat. Don't include the parentheses in your config.  Those are just my way of putting some inline notes in this example.

### Older Home Assistant installations (<0.88)
Copy 'lennox.py' from 'ha_component' to &lt;config directory&gt;/custom_components/climate and add the following to your configuration.yaml file:
```yaml
climate:
  - platform: lennox
    name: lennox
    username: !secret icomfort_username
    password: !secret icomfort_password
    system: 0 (optional, default = 0)
    zone: 0 (optional, default = 0)
    min_temp: 55 (optional, default = 45)
    max_temp: 90 (optional, default = 95)
```
Platform has to be 'lennox' but everything else is your's to customize. Don't include the parentheses in your config.  Those are just my way of putting some inline notes in this example.


# Notes
If I can figure out how to talk to the thermostat directly I will add that code here as well, but I don't have a lot of hope for that at the moment.  If I get really bored, maybe I could build a fake local cloud server and force my thermostat to talk to it.


# Credits
My code is built on the work of Jerome Avondo (ut666)
* API: https://github.com/ut666/LennoxPy
* HA Component: https://github.com/ut666/Homeassistant/tree/master/custom_components/climate
* Lennox Cloud API details: https://github.com/ut666/LennoxThermoPi-II
