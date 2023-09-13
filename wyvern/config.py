# -*- coding: utf-8 -*-
from pydantic import BaseSettings

from wyvern.experimentation.providers.base import ExperimentationProvider


class Settings(BaseSettings):
    """Settings for the Wyvern service

    Extends from BaseSettings class, allowing values to be overridden by environment variables. This is useful
    in production for secrets you do not wish to save in code

    Attributes:
        ENVIRONMENT: The environment the service is running in. Default to `development`.
        PROJECT_NAME: The name of the project. Default to `default`.
        REDIS_HOST: The host of the redis instance. Default to `localhost`.
        REDIS_PORT: The port of the redis instance. Default to `6379`.

        WYVERN_API_KEY: The API key for the Wyvern API. Default to `""`, empty string.
        WYVERN_BASE_URL: The base url of the Wyvern API. Default to `https://api.wyvern.ai`
        WYVERN_ONLINE_FEATURES_PATH:
            The path to the online features endpoint. Default to `/feature/get-online-features`.
        WYVERN_HISTORICAL_FEATURES_PATH:
            The path to the historical features endpoint. Default to `/feature/get-historical-features`.
        WYVERN_FEATURE_STORE_URL: The url of the Wyvern feature store. Default to `https://api.wyvern.ai`.

        SNOWFLAKE_ACCOUNT: The account name of the Snowflake instance. Default to `""`, empty string.
        SNOWFLAKE_USER: The username of the Snowflake instance. Default to `""`, empty string.
        SNOWFLAKE_PASSWORD: The password of the Snowflake instance. Default to `""`, empty string.
        SNOWFLAKE_ROLE: The role of the Snowflake instance. Default to `""`, empty string.
        SNOWFLAKE_WAREHOUSE: The warehouse of the Snowflake instance. Default to `""`, empty string.
        SNOWFLAKE_DATABASE: The database of the Snowflake instance. Default to `""`, empty string.
        SNOWFLAKE_OFFLINE_STORE_SCHEMA: The schema of the Snowflake instance. Default to `PUBLIC`.

        AWS_ACCESS_KEY_ID: The access key id for the AWS instance. Default to `""`, empty string.
        AWS_SECRET_ACCESS_KEY: The secret access key for the AWS instance. Default to `""`, empty string.
        AWS_REGION_NAME: The region name for the AWS instance. Default to `us-east-1`.

        FEATURE_STORE_TIMEOUT: The timeout for the feature store. Default to `60` seconds.
        SERVER_TIMEOUT: The timeout for the server. Default to `60` seconds.

        REDIS_BATCH_SIZE: The batch size for the redis instance. Default to `100`.
        WYVERN_INDEX_VERSION: The version of the Wyvern index. Default to `1`.
        MODELBIT_BATCH_SIZE: The batch size for the modelbit. Default to `30`.

        EXPERIMENTATION_ENABLED: Whether experimentation is enabled. Default to `False`.
        EXPERIMENTATION_PROVIDER: The experimentation provider. Default to `ExperimentationProvider.EPPO.value`.
        EPPO_API_KEY: The API key for EPPO (an experimentation provider). Default to `""`, empty string.

        FEATURE_STORE_ENABLED: Whether the feature store is enabled. Default to `True`.
        EVENT_LOGGING_ENABLED: Whether event logging is enabled. Default to `True`.
    """

    ENVIRONMENT: str = "development"

    PROJECT_NAME: str = "default"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # URLs
    WYVERN_BASE_URL = "https://api.wyvern.ai"
    WYVERN_ONLINE_FEATURES_PATH: str = "/feature/get-online-features"
    WYVERN_HISTORICAL_FEATURES_PATH: str = "/feature/get-historical-features"
    WYVERN_FEATURE_STORE_URL: str = "https://api.wyvern.ai"

    WYVERN_API_KEY: str = ""

    # Snowflake configurations
    SNOWFLAKE_ACCOUNT: str = ""
    SNOWFLAKE_USER: str = ""
    SNOWFLAKE_PASSWORD: str = ""
    SNOWFLAKE_ROLE: str = ""
    SNOWFLAKE_WAREHOUSE: str = ""
    SNOWFLAKE_DATABASE: str = ""
    SNOWFLAKE_OFFLINE_STORE_SCHEMA: str = "PUBLIC"
    SNOWFLAKE_REALTIME_FEATURE_LOG_TABLE: str = "FEATURE_LOGS"

    # NOTE: aws configs are used for feature logging with AWS firehose
    AWS_ACCESS_KEY_ID: str = ""
    AWS_SECRET_ACCESS_KEY: str = ""
    AWS_REGION_NAME: str = "us-east-1"

    FEATURE_STORE_TIMEOUT: int = 60
    SERVER_TIMEOUT: int = 60

    # pipeline service configurations
    REDIS_BATCH_SIZE: int = 100

    WYVERN_INDEX_VERSION: int = 1

    MODELBIT_BATCH_SIZE: int = 30
    MODEL_BATCH_SIZE: int = 30

    # experimentation configurations
    EXPERIMENTATION_ENABLED: bool = False
    EXPERIMENTATION_PROVIDER: str = ExperimentationProvider.EPPO.value
    EPPO_API_KEY: str = ""

    # wyvern component flag
    FEATURE_STORE_ENABLED: bool = True
    EVENT_LOGGING_ENABLED: bool = True

    class Config:
        env_file = (".env", ".env.prod")
        env_file_encoding = "utf-8"


settings = Settings()
