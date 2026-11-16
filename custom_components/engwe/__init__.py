"""ENGWE cloud integration."""
from datetime import timedelta
import aiohttp
from homeassistant.const import CONF_EMAIL, CONF_PASSWORD, Platform
from homeassistant.exceptions import ConfigEntryAuthFailed
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from .const import BASE_URL, DOMAIN

PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR, Platform.DEVICE_TRACKER]

class EngweCoordinator(DataUpdateCoordinator):
    def __init__(self, hass, entry):
        super().__init__(hass, logger=__import__('logging').getLogger(__name__), name=DOMAIN, update_interval=timedelta(minutes=10))
        self.entry = entry
        self.session = async_get_clientsession(hass)
        self.token = None
        self.imei = None

    async def request(self, path, body, authenticated=True):
        headers = {"Authorization": self.token} if authenticated and self.token else {}
        try:
            async with self.session.post(BASE_URL + path, json=body, headers=headers, timeout=aiohttp.ClientTimeout(total=20)) as resp:
                if resp.status in (401, 403):
                    raise ConfigEntryAuthFailed("ENGWE rejected authentication")
                resp.raise_for_status()
                payload = await resp.json(content_type=None)
        except (aiohttp.ClientError, TimeoutError, ValueError) as exc:
            raise UpdateFailed("ENGWE request failed") from exc
        if not isinstance(payload, dict) or 'data' not in payload:
            raise UpdateFailed("Unexpected ENGWE response")
        if payload.get('code') not in (0, 200, '0', '200', None):
            raise UpdateFailed("ENGWE returned an application error")
        return payload['data']

    async def _async_update_data(self):
        if not self.token:
            data = await self.request('/api/app/user/login', {'email': self.entry.data[CONF_EMAIL], 'password': self.entry.data[CONF_PASSWORD], 'lang': 'en'}, False)
            if not isinstance(data, dict) or not data.get('token'):
                raise ConfigEntryAuthFailed('ENGWE login did not return a token')
            self.token = data['token']
        if not self.imei:
            bikes = await self.request('/api/app/bike/user-ebike', {'isDefult': 0})
            if not isinstance(bikes, list):
                raise UpdateFailed('Unexpected bicycle list response')
            iot_bikes = [bike for bike in bikes if isinstance(bike, dict) and bike.get('deviceImei')]
            if not iot_bikes:
                raise UpdateFailed('No IoT bicycle found on this account')
            selected = next((bike for bike in iot_bikes if bike.get('defultBike') == 1), iot_bikes[0])
            self.imei = selected['deviceImei']
        attributes = await self.request('/api/app/iot/device/attr/newest', {'imei': self.imei})
        info = await self.request('/api/app/iot/device/basicInfo', {'imei': self.imei})
        if not isinstance(attributes, list) or not isinstance(info, dict):
            raise UpdateFailed('Unexpected bicycle status response')
        return {'attributes': attributes, 'online': info.get('networkInfo', {}).get('isOnline')}

async def async_setup_entry(hass, entry):
    coordinator = EngweCoordinator(hass, entry)
    await coordinator.async_config_entry_first_refresh()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = coordinator
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True

async def async_unload_entry(hass, entry):
    if await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id, None)
        return True
    return False
