# Lennox iComfort WiFi Component
A custom component for Home Assistant to integrate with Lennox iComfort WiFi thermostats and AirEase Comfort Sync thermostats.

**Requirement:** You must have your thermostat linked to a myicomfort.com (Lennox) or mycomfortsync.com (AirEase) account for this integration to work.

> **Please Note:** This component **does not** support the Lennox iComfort S30 or Lennox iComfort E30 thermostats.  

## Basic Configuration
Add the integration from **Settings > Devices & services > Add integration** and
select **Lennox iComfort**. Enter an account, then select the systems and zones to
expose. Repeat the setup only for another account or cloud service.

Existing YAML configuration is imported automatically as config entries. After the
import, remove the old section from `configuration.yaml`:
```yaml
climate:
  - platform: myicomfort
    name: firstfloor
    username: !secret cloudapi_username
    password: !secret cloudapi_password
```

# Documentation
Please visit the [GitHub Repository](https://github.com/thevoltagesource/LennoxiComfort) for full documentation.
