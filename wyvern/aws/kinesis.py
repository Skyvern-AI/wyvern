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
    EVENT_STREAM = "event-stream"

    def get_stream_name(
        self,
        customer_specific: bool = True,
        env_specific: bool = True,
    ) -> str:
        stream_name = self.value
        if customer_specific:
            stream_name = f"{settings.PROJECT_NAME}-{stream_name}"

        if env_specific:
            # env_name = "production" if settings.ENVIRONMENT == "development" else settings.ENVIRONMENT
            env_name = settings.ENVIRONMENT
            stream_name = f"{stream_name}-{env_name}"

        return stream_name


class WyvernKinesisFirehose:
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
        if not records:
            return
        logger.info(
            f"Sending {len(records)} records to {stream_name.get_stream_name()}",
        )
        dict_records = [{"Data": record.json()} for record in records]

        record_chunks = [
            dict_records[i : (i + CHUNK_SIZE)]
            for i in range(0, len(dict_records), CHUNK_SIZE)
        ]
        for chunk in record_chunks:
            if settings.ENVIRONMENT == "development":
                logger.info(
                    "Not sending records to Kinesis Firehose in development mode.",
                )
                logger.debug(f"Records: {chunk}")
            else:
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


wyvern_kinesis_firehose = WyvernKinesisFirehose()
