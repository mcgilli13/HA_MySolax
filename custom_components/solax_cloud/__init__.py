# __init__.py – mit YAML-Unterstützung für deine Integration

import logging
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)
DOMAIN = "solax_cloud"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Set up the integration via YAML."""
    if DOMAIN not in config:
        return True

    # Extract token and wifi_sn from configuration.yaml
    token = config[DOMAIN].get("token")
    wifi_sn = config[DOMAIN].get("wifi_sn")

    if not token or not wifi_sn:
        _LOGGER.error("Missing token or wifi_sn in configuration.yaml")
        return False

    # Store in hass.data for use in sensor.py
    hass.data[DOMAIN] = {
        "token": token,
        "wifi_sn": wifi_sn,
    }

    return True