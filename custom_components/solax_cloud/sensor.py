# sensor.py – Defines SolaX sensors using the YAML-based setup

import logging
import aiohttp
import async_timeout
from datetime import datetime, timedelta

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, CoordinatorEntity

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(seconds=30)

API_URL = "https://global.solaxcloud.com/api/v2/dataAccess/realtimeInfo/get"

async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up SolaX sensors via YAML."""
    from . import DOMAIN
    token = hass.data[DOMAIN]["token"]
    wifi_sn = hass.data[DOMAIN]["wifi_sn"]

    coordinator = SolaxDataUpdateCoordinator(hass, token, wifi_sn)
    await coordinator.async_refresh()

    sensors = []
    for key, name, unit in [
        ("acpower", "AC Power", "W"),
        ("yieldtoday", "Yield Today", "kWh"),
        ("yieldtotal", "Yield Total", "kWh"),
        ("soc", "Battery SoC", "%"),
        ("batPower", "Battery Power", "W"),
        ("feedinpower", "Feed-in Power", "W"),
        ("feedinenergy", "Feed-in Energy", "kWh"),
        ("consumeenergy", "Consume Energy", "kWh"),
        ("powerdc1", "PV String 1", "W"),
        ("powerdc2", "PV String 2", "W"),
        ("powerdc3", "PV String 3", "W"),
        ("batStatus", "Battery Status", None),
        ("inverterStatus", "Inverter Status", None),
        ("uploadTime", "Upload Time", None)
    ]:
        sensors.append(SolaxSensor(coordinator, key, name, unit))

    sensors.append(SolaxStatusSensor(coordinator))
    sensors.append(SolaxTimestampSensor(coordinator))

    if async_add_entities:
        async_add_entities(sensors, update_before_add=True)
    else:
        _LOGGER.debug("Sensors created without async_add_entities (YAML setup mode)")

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
        self._last_status = "uninitialized"
        self._last_update = None

    async def _async_update_data(self):
        payload = {"wifiSn": self.wifi_sn}
        headers = {
            "Content-Type": "application/json",
            "tokenId": str(self.token),
            "User-Agent": "Mozilla/5.0"
        }
        try:
            async with async_timeout.timeout(10):
                async with aiohttp.ClientSession() as session:
                    async with session.post(API_URL, headers=headers, json=payload) as resp:
                        result = await resp.json()
                        if result.get("success"):
                            self._last_status = "OK"
                            self._last_update = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            return result["result"]
                        else:
                            self._last_status = result.get("exception", "Unknown error")
                            raise Exception(f"SolaX Cloud API error: {self._last_status}")
        except Exception as e:
            self._last_status = str(e)
            _LOGGER.error(f"SolaX API fetch failed: {e}")
            raise

class SolaxSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator, key, name, unit):
        super().__init__(coordinator)
        self._key = key
        self._attr_name = f"SolaX {name}"
        self._attr_native_unit_of_measurement = unit
        self._attr_unique_id = f"solax_{key}"
        self._attr_device_class = "energy" if unit == "kWh" else "power" if unit == "W" else None

    @property
    def native_value(self):
        return self.coordinator.data.get(self._key)

    @property
    def available(self):
        return self.coordinator.data.get(self._key) is not None

class SolaxStatusSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "SolaX API Status"
        self._attr_unique_id = "solax_status"

    @property
    def native_value(self):
        return self.coordinator._last_status

    @property
    def available(self):
        return True

class SolaxTimestampSensor(CoordinatorEntity, SensorEntity):
    def __init__(self, coordinator):
        super().__init__(coordinator)
        self._attr_name = "SolaX Last Update"
        self._attr_unique_id = "solax_last_update"

    @property
    def native_value(self):
        return self.coordinator._last_update or "never"

    @property
    def available(self):
        return True