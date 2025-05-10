# Basiskomponente für die Integration

import logging

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.typing import ConfigType

_LOGGER = logging.getLogger(__name__)

DOMAIN = "solax_cloud"

async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    """Nur YAML-Setup (nicht verwendet)."""
    return True

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Setup aus UI-Integration (später)."""
    return True

async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    return True
