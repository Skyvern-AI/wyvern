# -*- coding: utf-8 -*-
from ddtrace import tracer
from ddtrace.filters import FilterRequestsOnUrl

from wyvern.config import settings


def setup_tracing():
    """
    Setup tracing for Wyvern service. Tracing is disabled in development mode and for healthcheck requests.
    """
    tracer.configure(
        settings={
            "FILTERS": [
                FilterRequestsOnUrl(r"http://.*/healthcheck$"),
            ],
        },
    )

    if settings.ENVIRONMENT == "development":
        tracer.enabled = False
