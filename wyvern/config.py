# -*- coding: utf-8 -*-
from pydantic import BaseSettings

from wyvern.experimentation.providers.base import ExperimentationProvider


class Settings(BaseSettings):
    ENVIRONMENT: str = "development"

    PROJECT_NAME: str = "default"

    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379
    REDIS_SCOPE: str = "default"

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

    # experimentation configurations
    EXPERIMENTATION_ENABLED: bool = False
    EXPERIMENTATION_PROVIDER: str = ExperimentationProvider.EPPO
    EPPO_API_KEY: str = ""

    class Config:
        env_file = (".env", ".env.prod")
        env_file_encoding = "utf-8"


settings = Settings()
