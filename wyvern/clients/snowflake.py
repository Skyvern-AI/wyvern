# -*- coding: utf-8 -*-
import snowflake.connector

from wyvern.config import settings


def generate_snowflake_ctx() -> snowflake.connector.SnowflakeConnection:
    """
    Generate a Snowflake context from the settings
    """
    return snowflake.connector.connect(
        user=settings.SNOWFLAKE_USER,
        password=settings.SNOWFLAKE_PASSWORD,
        role=settings.SNOWFLAKE_ROLE,
        account=settings.SNOWFLAKE_ACCOUNT,
        warehouse=settings.SNOWFLAKE_WAREHOUSE,
        database=settings.SNOWFLAKE_DATABASE,
        schema=settings.SNOWFLAKE_OFFLINE_STORE_SCHEMA,
    )
