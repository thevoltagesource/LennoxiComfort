# Lennox iComfort WiFi Component
A custom component for Home Assistant to integrate with Lennox iComfort WiFi thermostats and AirEase Comfort Sync thermostats.

**Requirement:** You must have your thermostat linked to a myicomfort.com (Lennox) or mycomfortsync.com (AirEase) account for this integration to work.

> **Please Note:** This component **does not** support the Lennox iComfort S30 or Lennox iComfort E30 thermostats.  

## Basic Configuration
```yaml
climate:
  - platform: myicomfort
    name: firstfloor
    username: !secret cloudapi_username
    password: !secret cloudapi_password
```

# Documentation
Please visit the [GitHub Repository](https://github.com/thevoltagesource/LennoxiComfort) for full documentation.