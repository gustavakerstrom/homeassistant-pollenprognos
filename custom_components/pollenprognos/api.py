import asyncio
import logging
import socket
import urllib.parse
from sqlite3.dbapi2 import paramstyle
from typing import Dict

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

TIMEOUT = 10

_LOGGER: logging.Logger = logging.getLogger(__package__)

HEADERS = {
    "accept": "application/json"
}


class PollenApi:
    def __init__(self, hass: HomeAssistant, url) -> None:
        self._hass = hass
        self._url: str = url

    async def async_get_data(self) -> dict:
        """Get data from the API."""
        return await self.api_wrapper("get", self._url)

    async def async_get_data_with_params(self, query_params=dict) -> dict:
        """Get data from the API."""
        url_parts = urllib.parse.urlparse(self._url)
        query = dict(urllib.parse.parse_qsl(url_parts.query))
        query.update(query_params)
        url = url_parts._replace(query=urllib.parse.urlencode(query)).geturl()
        return await self.api_wrapper("get", url)

    async def api_wrapper(
            self, method: str, url: str, data: dict = {}, headers: dict = {}
    ) -> dict:
        """Get information from the API."""
        try:
            session = async_get_clientsession(self._hass)
            async with async_timeout.timeout(TIMEOUT):
                if method == "get":
                    response = await session.get(url, headers=headers)
                    return await response.json()

                elif method == "put":
                    await session.put(url, headers=headers, json=data)

                elif method == "patch":
                    await session.patch(url, headers=headers, json=data)

                elif method == "post":
                    await session.post(url, headers=headers, json=data)

        except asyncio.TimeoutError as exception:
            _LOGGER.error(
                "Timeout error fetching information from %s - %s",
                url,
                exception,
            )

        except (KeyError, TypeError) as exception:
            _LOGGER.error(
                "Error parsing information from %s - %s",
                url,
                exception,
            )
        except (aiohttp.ClientError, socket.gaierror) as exception:
            _LOGGER.error(
                "Error fetching information from %s - %s",
                url,
                exception,
            )
        except Exception as exception:  # pylint: disable=broad-except
            _LOGGER.error("Something really wrong happened! - %s", exception)
