"""The Lennox iComfort integration."""

from homeassistant.config_entries import SOURCE_IMPORT
from homeassistant.const import Platform

DOMAIN = "myicomfort"
PLATFORMS = [Platform.CLIMATE]


async def async_setup(hass, config):
    """Import legacy climate YAML configuration into config entries."""
    for platform_config in config.get("climate", []):
        if platform_config.get("platform") != DOMAIN:
            continue
        hass.async_create_task(
            hass.config_entries.flow.async_init(
                DOMAIN,
                context={"source": SOURCE_IMPORT},
                data=platform_config,
            )
        )
    return True


async def async_setup_entry(hass, entry):
    """Set up myicomfort from a config entry."""
    entry.async_on_unload(entry.add_update_listener(_async_update_listener))
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def _async_update_listener(hass, entry):
    """Reload the account after options are changed."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_migrate_entry(hass, config_entry):
    """Migrate older grouped config entries to one hub per zone."""
    data = dict(config_entry.data)
    if "zones" in data:
        zone = data["zones"][0]
        data.pop("zones")
        data.pop("systems", None)
        data.update(
            {
                "system": zone.get("system", 0),
                "zone": zone.get("zone", 0),
                "name": zone.get("name", data.get("name", "iComfort")),
                "min_temp": zone.get("min_temp", data.get("min_temp")),
                "max_temp": zone.get("max_temp", data.get("max_temp")),
            }
        )
    data.pop("platform", None)
    if data != config_entry.data or config_entry.version < 3:
        hass.config_entries.async_update_entry(
            config_entry, data=data, version=4
        )
    return True


async def async_unload_entry(hass, entry):
    """Unload a myicomfort config entry."""
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
