# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
from typing import List, Optional, Type

from dotenv import load_dotenv
from fastapi import FastAPI

from wyvern.components.api_route_component import APIRouteComponent
from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
)
from wyvern.components.index import (
    IndexDeleteComponent,
    IndexGetComponent,
    IndexUploadComponent,
)
from wyvern.web_frameworks.fastapi import WyvernFastapi


class WyvernService:
    """
    The class to define, generate and run a Wyvern service

    Attributes:
        host: The host to run the service on. Defaults to localhost.
        port: The port to run the service on. Defaults to 5000.
    """

    def __init__(
        self,
        *,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> None:
        self.host = host
        self.port = port
        self.service = WyvernFastapi(host=self.host, port=self.port)

    async def register_routes(
        self,
        route_components: List[Type[APIRouteComponent]],
    ) -> None:
        """
        Register the routes for the Wyvern service

        Args:
            route_components: The list of route components to register

        Returns:
            None
        """
        for route_component in route_components:
            await self.service.register_route(route_component=route_component)

    def _run(
        self,
    ) -> None:
        """
        Run the Wyvern service

        Returns:
            None
        """
        load_dotenv()
        self.service.run()

    @staticmethod
    def generate(
        *,
        route_components: Optional[List[Type[APIRouteComponent]]] = None,
        realtime_feature_components: Optional[
            List[Type[RealtimeFeatureComponent]]
        ] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> WyvernService:
        """
        Generate a Wyvern service

        Args:
            route_components: The list of route components to register. Defaults to None.
            realtime_feature_components: The list of realtime feature components to register. Defaults to None.
            host: The host to run the service on. Defaults to localhost.
            port: The port to run the service on. Defaults to 5000.

        Returns:
            WyvernService: The generated Wyvern service
        """
        route_components = route_components or []
        service = WyvernService(host=host, port=port)
        asyncio.run(
            service.register_routes(
                [
                    IndexDeleteComponent,
                    IndexGetComponent,
                    IndexUploadComponent,
                    *route_components,
                ],
            ),
        )
        return service

    @staticmethod
    def run(
        *,
        route_components: List[Type[APIRouteComponent]],
        realtime_feature_components: Optional[
            List[Type[RealtimeFeatureComponent]]
        ] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
    ):
        """
        Generate and run a Wyvern service

        Args:
            route_components: The list of route components to register
            realtime_feature_components: The list of realtime feature components to register. Defaults to None.
            host: The host to run the service on. Defaults to localhost.
            port: The port to run the service on. Defaults to 5000.

        Returns:
            None
        """
        service = WyvernService.generate(
            route_components=route_components,
            realtime_feature_components=realtime_feature_components,
            host=host,
            port=port,
        )
        service._run()

    @staticmethod
    def generate_app(
        *,
        route_components: Optional[List[Type[APIRouteComponent]]] = None,
        realtime_feature_components: Optional[
            List[Type[RealtimeFeatureComponent]]
        ] = None,
        host: str = "127.0.0.1",
        port: int = 5000,
    ) -> FastAPI:
        """
        Generate a Wyvern service and return the FastAPI app

        Args:
            route_components: The list of route components to register. Defaults to None.
            realtime_feature_components: The list of realtime feature components to register. Defaults to None.
            host (str, optional): The host to run the service on. Defaults to localhost.
            port (int, optional): The port to run the service on. Defaults to 5000.

        Returns:
            FastAPI: The generated FastAPI app
        """
        service = WyvernService.generate(
            route_components=route_components,
            realtime_feature_components=realtime_feature_components,
            host=host,
            port=port,
        )
        return service.service.app
