# -*- coding: utf-8 -*-
import logging

import aiohttp

from wyvern.exceptions import WyvernError

logger = logging.getLogger(__name__)
DEFAULT_REQUEST_TIMEOUT = 60
timeout = aiohttp.ClientTimeout(total=DEFAULT_REQUEST_TIMEOUT)


class AiohttpClientWrapper:
    """AiohttpClientWrapper is a singleton wrapper around aiohttp.ClientSession."""

    async_client = None

    def start(self):
        """Instantiate the client. Call from the FastAPI startup hook."""
        self.async_client = aiohttp.ClientSession(timeout=timeout)

    async def stop(self):
        """Gracefully shutdown. Call from FastAPI shutdown hook."""
        if not self.async_client:
            return
        if self.async_client and not self.async_client.closed:
            await self.async_client.close()
        self.async_client = None

    def __call__(self):
        """Calling the instantiated AiohttpClientWrapper returns the wrapped singleton."""
        # Ensure we don't use it if not started / running
        if self.async_client is None:
            raise WyvernError("AiohttpClientWrapper not started")

        return self.async_client


aiohttp_client = AiohttpClientWrapper()
"""
The aiohttp client singleton. Use this to make requests.

Example:
    ```python
    from wyvern.core.http import aiohttp_client
    aiohttp_client().get("https://www.wyvern.ai")
    ```
"""
