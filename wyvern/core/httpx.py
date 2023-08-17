# -*- coding: utf-8 -*-
import logging

import httpx

from wyvern.exceptions import WyvernError

logger = logging.getLogger(__name__)
DEFAULT_HTTPX_TIMEOUT = 60


class HTTPXClientWrapper:

    async_client = None

    def start(self):
        """Instantiate the client. Call from the FastAPI startup hook."""
        self.async_client = httpx.AsyncClient(timeout=DEFAULT_HTTPX_TIMEOUT)

    async def stop(self):
        """Gracefully shutdown. Call from FastAPI shutdown hook."""
        if not self.async_client:
            return
        if self.async_client and not self.async_client.is_closed:
            await self.async_client.aclose()
        self.async_client = None

    def __call__(self):
        """Calling the instantiated HTTPXClientWrapper returns the wrapped singleton."""
        # Ensure we don't use it if not started / running
        if self.async_client is None:
            raise WyvernError("HTTPXClientWrapper not started")

        return self.async_client


httpx_client = HTTPXClientWrapper()
