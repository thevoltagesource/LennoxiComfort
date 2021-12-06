# Lennox iComfort WiFi Component
A custom component for Home Assistant to integrate with Lennox iComfort WiFi thermostats and AirEase Comfort Sync thermostats.

[![hacs_badge](https://img.shields.io/badge/HACS-Default-orange.svg)](https://github.com/custom-components/hacs)

> **Please Note:** This component **does not** support the Lennox iComfort S30 or Lennox iComfort E30 thermostats. For those thermostats please check out [PeteRanger's repository](https://github.com/PeteRager/lennoxs30).

# Requirements

- Home Assistant >= 2021.4
- Thermostat linked to a myicomfort.com (Lennox) or mycomfortsync.com (AirEase) account

# Installation
This integration is available in HACS for ease of installation.  
If you wish to manually install this component, copy the 'myicomfort' folder and contents to &lt;HA config directory&gt;/custom_components/ 

# Configuration
### Example configuation
```yaml
climate:
  - platform: myicomfort
    name: firstfloor
    username: !secret cloudapi_username
    password: !secret cloudapi_password
    system: 0
    zone: 0
    min_temp: 55
    max_temp: 90
    cloud_svc: airease
```

### Platform Parameters
| Name | Type | Requirement | Default | Description |
| ---- | ---- | ----------- | ------- | ----------- |
| name | string | required | none | Entity name |
| username | string | required | none | Cloud service account username |
| password | string | required | none | Cloud service account password |
| system | integer | optional | `0` | Select the system for integration if you have multiple on the account. |
| zone | integer | optional | `0` | Select the zone for integration if the selected system has multiple zones. |
| min_temp | integer | optional | `45` | Minimum temperature HA can set. |
| max_temp | integer | optional | `95` | Maximum temperature HA can set. |
| cloud_svc | string | optional | `lennox` | Cloud service selection - use `lennox` or `airease` | 

### Multiple zones or systems
Add additional entries under climate for each additional system or zone.
```yaml
climate:
  - platform: myicomfort
    name: Downstairs
    username: !secret cloudapi_username
    password: !secret cloudapi_password
    system: 0 
    zone: 0 
    min_temp: 55
    max_temp: 90
    cloud_svc: lennox
  - platform: myicomfort
    name: ManCave
    username: !secret cloudapi_username
    password: !secret cloudapi_password
    system: 0 
    zone: 1 
    min_temp: 45
    max_temp: 75
    cloud_svc: lennox
  - platform: myicomfort
    name: Upstairs
    username: !secret cloudapi_username
    password: !secret cloudapi_password
    system: 1 
    zone: 0 
    min_temp: 65
    max_temp: 80
    cloud_svc: airease
```

# Notes

### Humidity 
The humidity is exposed to HA as an attribute of the climate entity but since the device doesn't support set_humdity, most of the thermostat cards won't display it. The template platform can be used to capture the humidity and make it accessible as a sensor. You can use the [Simple Thermostat card](https://github.com/nervetattoo/simple-thermostat) to add the sensor to a thermostat card.

Below is a an example to expose the current humidity as a sensor. The climate device is named 'lennox' and the resulting sensor is 'lennox_humidity'.
```yaml
platform: template
sensors:
  lennox_humidity:
    value_template: "{{states.climate.lennox.attributes.current_humidity | float}}"
    friendly_name: "Humidity"
    unit_of_measurement: '%'
```

### HA 0.96 to 2021.4 
There were minor changes to the climate platform between 0.96 and 2021.4. You can read thru release notes in this repository to find a version that works for you.

### HA 0.95 or older
If for some reason you are still running HA 0.95 or older, you can still integrate with your thermostat. You just need to grab one of the older code sets from here: https://github.com/thevoltagesource/LennoxiComfort-archive

# Credits
My code is built on the work of Jerome Avondo (ut666)
- API: https://github.com/ut666/LennoxPy
- HA Component: https://github.com/ut666/Homeassistant/tree/master/custom_components/climate
- Lennox Cloud API details: https://github.com/ut666/LennoxThermoPi-II
