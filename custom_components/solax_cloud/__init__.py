# __init__.py – Home Assistant custom integration for SolaX Cloud (YAML-based setup)

import logging
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "solax_cloud"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up SolaX Cloud integration via YAML."""
    if DOMAIN not in config:
        return True

    token = config[DOMAIN].get("token")
    wifi_sn = config[DOMAIN].get("wifi_sn")

    if not token or not wifi_sn:
        _LOGGER.error("Missing token or wifi_sn in configuration.yaml")
        return False

    hass.data[DOMAIN] = {
        "token": token,
        "wifi_sn": wifi_sn,
    }

    from .sensor import async_setup_platform
    await async_setup_platform(hass, config[DOMAIN], None)

    return True

async def async_setup_entry(hass, entry):
    return True

async def async_unload_entry(hass, entry):
    return True