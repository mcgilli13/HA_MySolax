# sensor.py - Fetches and exposes SolaX Cloud v2 data as Home Assistant sensors

import logging
import aiohttp
import async_timeout
from datetime import timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
)
from homeassistant.helpers.entity import EntityCategory
from homeassistant.helpers.typing import HomeAssistantType, ConfigType

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=60)

API_URL = "https://global.solaxcloud.com/api/v2/dataAccess/realtimeInfo/get"

async def async_setup_platform(hass: HomeAssistantType, config: ConfigType, async_add_entities, discovery_info=None):
    """Set up the SolaX Cloud sensor platform."""
    token = hass.data.get("solax_cloud_token")
    wifi_sn = hass.data.get("solax_cloud_sn")

    if not token or not wifi_sn:
        _LOGGER.error("Missing token or WiFi SN for SolaX Cloud integration.")
        return

    coordinator = SolaxDataUpdateCoordinator(hass, token, wifi_sn)
    await coordinator.async_config_entry_first_refresh()

    async_add_entities([
        SolaxSensor(coordinator, "acpower", "AC Power", "W"),
        SolaxSensor(coordinator, "yieldtoday", "Yield Today", "kWh"),
        SolaxSensor(coordinator, "soc", "Battery SoC", "%")
    ])

class SolaxDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, token, wifi_sn):
        super().__init__(
            hass,
            _LOGGER,
            name="SolaX Cloud Coordinator",
            update_interval=SCAN_INTERVAL,
        )
        self.token = token
        self.wifi_sn = wifi_sn
        self.data = {}

    async def _async_update_data(self):
        payload = {"wifiSn": self.wifi_sn}
        headers = {
            "Content-Type": "application/json",
            "tokenId": self.token,
            "User-Agent": "Mozilla/5.0"
        }
        async with async_timeout.timeout(10):
            async with aiohttp.ClientSession() as session:
                async with session.post(API_URL, headers=headers, json=payload) as resp:
                    result = await resp.json()
                    if result.get("success"):
                        return result["result"]
                    raise Exception("Failed to fetch SolaX Cloud data: %s" % result.get("exception"))

class SolaxSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"solax_{key}"
        self._attr_device_class = "energy" if unit == "kWh" else "power" if unit == "W" else None
        self._attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def available(self):
        return self.coordinator.data.get(self._key) is not None
