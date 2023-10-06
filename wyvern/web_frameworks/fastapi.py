# -*- coding: utf-8 -*-
import logging
import time
from contextlib import asynccontextmanager
from typing import Annotated, Dict, Type, Union

import uvicorn
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from wyvern import request_context
from wyvern.aws.kinesis import KinesisFirehoseStream, wyvern_kinesis_firehose
from wyvern.components.api_route_component import APIRouteComponent
from wyvern.config import settings
from wyvern.core.http import aiohttp_client
from wyvern.entities.request import BaseWyvernRequest
from wyvern.event_logging import event_logger
from wyvern.exceptions import WyvernError, WyvernRouteRegistrationError
from wyvern.wyvern_request import WyvernRequest

logger = logging.getLogger(__name__)


def _dedupe_slash(path: str) -> str:
    """
    Remove duplicate slashes from a path.
    """
    return path.replace("//", "/")


def _massage_path(path: str) -> str:
    """
    Massage a path to be suitable for use in a URL.
    """
    massaged_path = _dedupe_slash(path)
    if massaged_path and massaged_path[0] != "/":
        massaged_path = "/" + massaged_path
    if massaged_path and massaged_path[-1] == "/":
        massaged_path = massaged_path[:-1]
    return massaged_path


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    A context manager that starts and stops with the app. This is used to start and stop the aiohttp client.
    """
    try:
        aiohttp_client.start()
        yield
    finally:
        await aiohttp_client.stop()


class WyvernFastapi:
    """
    A wrapper around FastAPI that provides a few additional features:
    - A healthcheck endpoint
    - A request middleware that logs the request and response payloads
    - A request middleware that sets the WyvernRequest in the request context
    - Auto registration of routes from APIRouteComponent subclasses

    endpoint input:
        the built WyvernPipeline
        the request input schema
        the request output schema
    """

    def __init__(self, host: str = "127.0.0.1", port: int = 8000) -> None:
        self.app = FastAPI(lifespan=lifespan)
        self.host = host
        self.port = port

        @self.app.get("/healthcheck")
        async def healthcheck() -> Dict[str, str]:
            return {"status": "OK"}

        @self.app.middleware("http")
        async def request_middleware(request: Request, call_next):
            start_time = time.time()
            response = await call_next(request)
            if request.url.path == "/healthcheck":
                return response
            process_time_ms = (time.time() - start_time) * 1000
            logger.info(
                f"process_time={process_time_ms} ms, "
                f"method={request.method}, url={request.url.path}, status_code={response.status_code}",
            )
            return response

    async def register_route(
        self,
        route_component: Union[Type[APIRouteComponent], APIRouteComponent],
    ) -> None:
        """
        Register a route component. This will register the route with FastAPI and also initialize the route component.

        Args:
            route_component: The route component to register.

        Raises:
            WyvernRouteRegistrationError: If the route component is not a subclass of APIRouteComponent.
        """
        if isinstance(route_component, APIRouteComponent):
            root_component = route_component
        elif not issubclass(route_component, APIRouteComponent):
            raise WyvernRouteRegistrationError(component=route_component)
        else:
            root_component = route_component()
        await root_component.initialize_wrapper()
        path = _massage_path(f"/api/{root_component.API_VERSION}/{root_component.PATH}")

        @self.app.post(
            path,
            response_model=root_component.RESPONSE_SCHEMA_CLASS,
            response_model_exclude_none=True,
            name=root_component.api_name,
        )
        async def post(
            data: root_component.REQUEST_SCHEMA_CLASS,  # type: ignore
            fastapi_request: Request,
            background_tasks: BackgroundTasks,
            x_wyvern_run_id: Annotated[
                int,
                Header(),
            ] = 0,
        ) -> root_component.RESPONSE_SCHEMA_CLASS:  # type: ignore
            """
            The main entrypoint for the route component. This will parse the request payload, set the WyvernRequest in
            the request context, warm up the route component, execute the route component, and log the events to
            Kinesis Firehose in the background.

            Args:
                data: The request payload.
                fastapi_request: The FastAPI request object.
                background_tasks: The FastAPI background tasks object.

            Returns:
                The response payload.
            """
            json = await fastapi_request.json()
            try:
                # from pyinstrument import Profiler
                # profiler = Profiler(async_mode="enabled")
                # profiler.start()
                request_id = None
                if isinstance(data, BaseWyvernRequest):
                    request_id = data.request_id

                wyvern_req = WyvernRequest.parse_fastapi_request(
                    json=data,
                    req=fastapi_request,
                    request_id=request_id,
                    run_id=str(x_wyvern_run_id),
                )
                request_context.set(wyvern_req)

                await root_component.warm_up(data)
                output = await root_component.execute(data)

                background_tasks.add_task(
                    wyvern_kinesis_firehose.put_record_batch_callable,
                    KinesisFirehoseStream.EVENT_STREAM,
                    # TODO (suchintan): "invariant" list error
                    event_logger.get_logged_events_generator(),  # type: ignore
                )

                # profiler.stop()
                # profiler.print(show_all=True)
            except ValidationError as e:
                logger.exception(f"Validation error error={e} request_payload={json}")
                raise HTTPException(status_code=422, detail=e.errors())
            except WyvernError as e:
                logger.warning(f"Wyvern error error={e} request_payload={json}")
                return JSONResponse(
                    status_code=400,
                    content={
                        "detail": str(e),
                        "error_code": e.error_code,
                    },
                )
            except Exception as e:
                logger.exception(f"Unexpected error error={e} request_payload={json}")
                raise HTTPException(status_code=500, detail=str(e))
            finally:
                request_context.reset()
            if not output:
                raise HTTPException(status_code=500, detail="something is wrong")
            logger.info(
                f"path={path}, request_payload={json}, response_payload={output}",
            )
            return output

    def run(self) -> None:
        config = uvicorn.Config(
            self.app,
            host=self.host,
            port=self.port,
            timeout_keep_alive=settings.SERVER_TIMEOUT,
        )
        uvicorn_server = uvicorn.Server(config=config)
        uvicorn_server.run()
