# -*- coding: utf-8 -*-
import importlib.metadata
import platform
from typing import Any, Dict, Optional

from posthog import Posthog

from wyvern.config import settings

posthog = Posthog(
    "phc_bVT2ugnZhMHRWqMvSRHPdeTjaPxQqT3QSsI3r5FlQR5",
    host="https://app.posthog.com",
    disable_geoip=False,
)


def get_oss_version() -> str:
    try:
        return importlib.metadata.version("wyvern-ai")
    except Exception:
        return "unknown"


def analytics_metadata() -> Dict[str, Any]:
    return {
        "os": platform.system().lower(),
        "oss_version": get_oss_version(),
        "machine": platform.machine(),
        "platform": platform.platform(),
        "python_version": platform.python_version(),
        "environment": settings.ENVIRONMENT,
    }


def capture(
    event: str,
    distinct_id: str = "oss",
    data: Optional[Dict[str, Any]] = None,
) -> None:
    try:
        data = data or {}
        data.update(analytics_metadata())
        posthog.capture(
            distinct_id=distinct_id,
            event=event,
            properties=data,
        )
    except Exception as e:
        posthog.capture(
            distinct_id=distinct_id,
            event="failure",
            properties={
                "capture_error": str(e),
            },
        )
