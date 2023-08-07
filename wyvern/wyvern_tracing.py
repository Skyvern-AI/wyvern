# -*- coding: utf-8 -*-
from ddtrace import tracer
from ddtrace.filters import FilterRequestsOnUrl


def setup_tracing():
    tracer.configure(
        settings={
            "FILTERS": [
                FilterRequestsOnUrl(r"http://.*/healthcheck$"),
            ],
        },
    )
