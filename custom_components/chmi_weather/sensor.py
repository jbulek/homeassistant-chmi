import logging
from datetime import datetime, timedelta
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import STATIONS, SENSOR_TYPES, SENSOR_UNITS, DOMAIN, SENSOR_ICONS

_LOGGER = logging.getLogger(__name__)
SCAN_INTERVAL = timedelta(minutes=10)


class CHMIDataUpdateCoordinator(DataUpdateCoordinator):
    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self._entry = entry
        self._station_key = entry.data["station_key"]
        station = STATIONS[self._station_key]
        self._station_id = station["station_id"]
        self._station_type = station["station_type"]
        self._session = async_get_clientsession(hass)
        super().__init__(
            hass,
            _LOGGER,
            name="CHMI Data",
            update_method=self._async_update_data,
            update_interval=SCAN_INTERVAL,
        )

    async def _async_update_data(self):
        for offset in [0, -1]:  # Try today, then yesterday
            date = (datetime.utcnow() + timedelta(days=offset)).strftime("%Y%m%d")
            url = (
                "https://opendata.chmi.cz/meteorology/climate/now/data/"
                f"10m-0-{self._station_type}-0-{self._station_id}-{date}.json"
            )

            try:
                async with self._session.get(url) as response:
                    if response.status == 200:
                        raw = await response.json()
                        return parse_weather_data(raw)
                    _LOGGER.warning(f"CHMI data not available for date {date} (HTTP {response.status})")
            except Exception as e:
                _LOGGER.error(f"Error fetching CHMI data for {date}: {e}")

        raise UpdateFailed("No valid CHMI weather data available.")


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
):
    entry_data = hass.data[DOMAIN][entry.entry_id]
    coordinator = entry_data["coordinator"]
    station_key = entry.data["station_key"]

    sensors = [
        WeatherSensor(coordinator, key, SENSOR_TYPES[key], SENSOR_UNITS.get(key), station_key)
        for key in SENSOR_TYPES
        if key in coordinator.data
    ]
    async_add_entities(sensors)


def parse_weather_data(json_data):
    latest = {}
    try:
        values = json_data["data"]["data"]["values"]
        for entry in values:
            element = entry[1]
            dt_str = entry[2]
            value = entry[3]

            try:
                dt = datetime.fromisoformat(dt_str.replace("Z", "+00:00"))
            except ValueError:
                continue

            if element not in latest or dt > latest[element]["dt"]:
                latest[element] = {
                    "dt": dt,
                    "value": value
                }
    except Exception as e:
        _LOGGER.error(f"Error parsing weather data: {e}")

    return latest


class WeatherSensor(Entity):
    def __init__(self, coordinator, key, name, unit, station_key):
        self.coordinator = coordinator
        self._key = key
        self._name = name
        self._unit = unit
        self._station_key = station_key

    @property
    def name(self):
        return f"{self._station_key} {self._name}"

    @property
    def state(self):
        item = self.coordinator.data.get(self._key)
        return item["value"] if item else None

    @property
    def available(self):
        return self.coordinator.last_update_success

    @property
    def unique_id(self):
        return f"{DOMAIN}_{self._station_key.lower()}_{self._key}"

    @property
    def unit_of_measurement(self):
        return self._unit

    @property
    def icon(self):
        return SENSOR_ICONS.get(self._key, "mdi:weather-partly-cloudy")

    @property
    def extra_state_attributes(self):
        item = self.coordinator.data.get(self._key)
        if item:
            return {
                "last_update": item["dt"].isoformat()
            }
        return {}

    async def async_update(self):
        await self.coordinator.async_request_refresh()
