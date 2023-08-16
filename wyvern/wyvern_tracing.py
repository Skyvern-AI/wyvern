# -*- coding: utf-8 -*-
from ddtrace import tracer
from ddtrace.filters import FilterRequestsOnUrl

from wyvern.config import settings


def setup_tracing():
    tracer.configure(
        settings={
            "FILTERS": [
                FilterRequestsOnUrl(r"http://.*/healthcheck$"),
            ],
        },
    )

    if settings.ENVIRONMENT == "development":
        tracer.enabled = False
