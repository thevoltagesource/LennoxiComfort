# Lennox iComfort WiFi Component
This code set is my custom component for Home Assistant to integrate with a Lennox iComfort WiFi thermostat. This code only works with the iComfort WiFi and not the iComfort S30 or E30.  To help with the distiction and avoid any head banging, I am renaming the component from lennox to myicomfort. To use this code you must have previously created a myicomfort account and connected your iComfort WiFi thermostat to your account. 

Home Assistant made an architecture change in version 0.88 which has me revamping this respoitory. Please make sure to follow the steps for the version you are running.  I took this opportunity to change the component name.

The API code used to interface with myicomfort.com has been published to PyPI and HA will install the appropriate version on startup the first time the component is loaded.  You no longer need to manually copy the API code to your installation.  If you previously copied lennox_api.py to your installation it is safe to delete this file now.

### Home Assistant 0.96 and newer
Copy the 'myicomfort' folder and contents to &lt;config directory&gt;/custom_components/ and add the following to your configuration.yaml file:
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
Platform has to be 'myicomfort' but everything else is your's to customize. Don't include the parentheses in your config.  Those are just my way of putting some inline notes in this example.

### Home Assistant 0.88 to 0.95
This setup is just like the current code (>= 0.96) but HA overhauled the climate integration in 0.96 resulting in breaking changes. If you are still running a version of HA in this range, you can find working code in an old commit. I should figure out how to do releases so this is easier in the future.  If you need help, please feel free to send me a message.

### Older Home Assistant installations (<0.88)
Copy 'lennox.py' from 'ha_component' &lt;config directory&gt;/custom_components/climate and add the following to your configuration.yaml file:
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
