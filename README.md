# Lennox iComfort
Python code used for interacting with the Lennox iComfort cloud service and connecting my the thermostat to Home Assistant.

The code in /api is for interacting with the Lennox iComfot Cloud API to read data from the thermostat and change settings. I only have one thermostat and one zone so I am limited on some of the more complex possibilities.  This is a required piece for the HA component

The code in /ha_componenet is the Home Assistant climate component

If I can figure out how to talk to the thermostat directly I will add that code here as well, but I don't have a lot of hope for that at the moment.  If I get really bored, maybe I could build a fake local cloud server and force my thermostat to talk to it.


# Credit
My code is built on the work of Jarome Avondo (ut666)
API: https://github.com/ut666/LennoxPy
HA Component: https://github.com/ut666/Homeassistant/tree/master/custom_components/climate
Lennox Cloud API details: https://github.com/ut666/LennoxThermoPi-II
