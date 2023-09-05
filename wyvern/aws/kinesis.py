# -*- coding: utf-8 -*-
import logging
import traceback
from enum import Enum
from typing import Callable, List

import boto3
from ddtrace import tracer
from pydantic import BaseModel

from wyvern.config import settings

logger = logging.getLogger(__name__)

CHUNK_SIZE = 100


class KinesisFirehoseStream(str, Enum):
    """
    Enum for Kinesis Firehose stream names

    Usage:
    ```
    >>> KinesisFirehoseStream.EVENT_STREAM.get_stream_name()
    ```
    """

    EVENT_STREAM = "event-stream"

    def get_stream_name(
        self,
        customer_specific: bool = True,
        env_specific: bool = True,
    ) -> str:
        """
        Returns the stream name for the given stream

        Args:
            customer_specific: Whether the stream name should be customer specific
            env_specific: Whether the stream name should be environment specific

        Returns:
            The stream name
        """
        stream_name = self.value
        if customer_specific:
            stream_name = f"{settings.PROJECT_NAME}-{stream_name}"

        if env_specific:
            env_name = settings.ENVIRONMENT
            stream_name = f"{stream_name}-{env_name}"

        return stream_name


class WyvernKinesisFirehose:
    """
    Wrapper around boto3 Kinesis Firehose client
    """

    def __init__(self):
        self.firehose_client = boto3.client(
            "firehose",
            aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
            aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
            region_name=settings.AWS_REGION_NAME,
        )

    def put_record_batch_callable(
        self,
        stream_name: KinesisFirehoseStream,
        record_generator: List[Callable[[], List[BaseModel]]],
    ):
        """
        Puts records to the given stream. This is a callable that can be used with FastAPI's BackgroundTasks. This
        way events can be logged asynchronously after the response is sent to the client.

        Args:
            stream_name (KinesisFirehoseStream): The stream to put records to
            record_generator (List[Callable[[], List[BaseModel]]]): A list of functions that return a list of records

        Returns:
            None
        """
        with tracer.trace("flush_records_to_kinesis_firehose"):
            records = [
                record
                for record_generator in record_generator
                for record in record_generator()
            ]
            self.put_record_batch(stream_name, records)

    def put_record_batch(
        self,
        stream_name: KinesisFirehoseStream,
        records: List[BaseModel],
    ):
        """
        Puts records to the given stream

        Args:
            stream_name (KinesisFirehoseStream): The stream to put records to
            records (List[BaseModel]): A list of records

        Returns:
            None
        """
        if not records:
            return
        dict_records = [{"Data": record.json()} for record in records]

        record_chunks = [
            dict_records[i : (i + CHUNK_SIZE)]
            for i in range(0, len(dict_records), CHUNK_SIZE)
        ]
        for chunk in record_chunks:
            if settings.EVENT_LOGGING_ENABLED and settings.ENVIRONMENT != "development":
                try:
                    self.firehose_client.put_record_batch(
                        DeliveryStreamName=stream_name.get_stream_name(),
                        Records=chunk,
                    )
                except Exception:
                    logger.exception(
                        "Failed to put records to kinesis firehose",
                        traceback.format_exc(),
                    )
            else:
                logger.debug(
                    "Logging disabled. Not sending records to Kinesis Firehose. Records: {chunk}",
                )


wyvern_kinesis_firehose = WyvernKinesisFirehose()
