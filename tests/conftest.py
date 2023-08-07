# -*- coding: utf-8 -*-
import pytest
from ddtrace import tracer


@pytest.fixture(scope="session", autouse=True)
def disable_ddtrace():
    tracer.enabled = False
