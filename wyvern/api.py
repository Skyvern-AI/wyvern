# -*- coding: utf-8 -*-
from __future__ import annotations

import asyncio
from functools import wraps
from typing import Any, Callable, Dict, Hashable, List, Optional, Union

import aiohttp
import nest_asyncio
import pandas as pd
import requests
from pandas.api.types import is_datetime64_any_dtype
from tqdm import tqdm

from wyvern.config import settings
from wyvern.exceptions import WyvernAPIKeyMissingError, WyvernError

BATCH_SIZE = 15000
HTTP_TIMEOUT = 180
BATCH_SIZE_PER_GATHER = 4
RETRY_PER_BATCH = 2


def ensure_async_client(func: Callable) -> Callable:
    """
    Ensure that the async client is open before calling the function and close it after calling the function

    Args:
        func: The function to be wrapped

    Returns:
        The wrapped function
    """

    @wraps(func)
    def wrapper(self: WyvernAPI, *args, **kwargs):
        if self.async_client.closed:
            self.async_client = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
            )
        try:
            return func(self, *args, **kwargs)
        finally:
            if not self.async_client.closed:
                asyncio.run(self.async_client.close())

    return wrapper


class WyvernAPI:
    """
    Wyvern API client
    """

    def __init__(
        self,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        batch_size: int = BATCH_SIZE,
    ) -> None:
        api_key = api_key or settings.WYVERN_API_KEY
        if not api_key:
            raise WyvernAPIKeyMissingError()
        self.headers = {"x-api-key": api_key}
        self.base_url = base_url or settings.WYVERN_BASE_URL
        self.batch_size = batch_size
        self.async_client = aiohttp.ClientSession(
            timeout=aiohttp.ClientTimeout(total=HTTP_TIMEOUT),
        )

    def get_online_features(
        self,
        features: List[str],
        entities: Dict[str, List[Any]],
        get_event_timestamps: bool = False,
        get_feature_statuses: bool = False,
    ) -> pd.DataFrame:
        request = {"features": features, "entities": entities}
        response = self._send_request_to_wyvern_api(
            settings.WYVERN_ONLINE_FEATURES_PATH,
            data=request,
        )

        return self._convert_online_features_to_df(
            response,
            get_feature_statuses,
            get_event_timestamps,
        )

    @ensure_async_client
    def get_historical_features(
        self,
        features: List[str],
        entities: Union[Dict[Hashable, List[Any]], pd.DataFrame],
    ) -> pd.DataFrame:
        """
        Aggregate all the historical features, including the offline features in your data warehouse
        and the historical real-time features being consumed by wyvern pipeline.

        Args:
            features: A list of feature names.
            entities: A dictionary or pandas DataFrame of entity names and their values.
                some requirements of entities:
                - entities must have request and timestamp keys
                - request is a list of the request_id of request getting into Wyvern's pipeline
                - timestamp is a list of timestamp of the request
                - the rest of the columns are the entity for the features and the user interaction data
        Returns:
            A pandas DataFrame with all the feature data you're requesting from the entities.
        """
        # nest_asyncio call is needed to avoid RuntimeError: This event loop is already running with notebook use case
        nest_asyncio.apply()
        if isinstance(entities, dict):
            entities = pd.DataFrame(entities)

        # build the new name to old name mapping
        lower_case_column_to_old_column: Dict[str, str] = {
            column.lower(): column for column in entities.columns
        }
        lower_case_feature_to_old_feature: Dict[str, str] = {
            feature.replace(":", "__", 1).lower(): feature for feature in features
        }

        # all entities name will be lower case when passing to the wyvern API
        entities = entities.rename(columns=str.lower)

        for column in entities.columns:
            if is_datetime64_any_dtype(entities[column]):
                entities[column] = entities[column].astype(str)

        entities = entities.to_dict(orient="list")

        # validate data first
        # 1. make sure "request" is in entities
        if "request" not in entities:
            raise ValueError("entities must contain 'request' key")
        if "timestamp" not in entities:
            raise ValueError("entities must contain 'timestamp' key")
        timestamps = entities["timestamp"]
        timestamps_length = len(timestamps)
        for key, value in entities.items():
            if len(value) != timestamps_length:
                raise ValueError(
                    f"Length of entity '{key}' ({len(value)}) does "
                    f"not match length of timestamp ({timestamps_length})",
                )
        # Split data into batches with up to 2000 items per batch
        num_batches = (timestamps_length + self.batch_size - 1) // self.batch_size
        data_batches = []
        for i in range(num_batches):
            start_idx = i * self.batch_size
            end_idx = min((i + 1) * self.batch_size, timestamps_length)
            batch_entities = {
                key: value[start_idx:end_idx] for key, value in entities.items()
            }
            batch_timestamps = timestamps[start_idx:end_idx]
            data_batches.append(
                {
                    "features": features,
                    "entities": batch_entities,
                    "timestamps": batch_timestamps,
                },
            )

        # Send requests for each batch and concatenate the responses
        responses: list[pd.DataFrame] = []
        num_gathers = (num_batches + BATCH_SIZE_PER_GATHER - 1) // BATCH_SIZE_PER_GATHER
        progress_bar = tqdm(
            total=len(data_batches),
            desc="Fetching historical data",
            unit="batch",
        )
        for i in range(num_gathers):
            start_idx = i * BATCH_SIZE_PER_GATHER
            end_idx = min((i + 1) * BATCH_SIZE_PER_GATHER, num_batches)
            retry_count = 0
            while retry_count < RETRY_PER_BATCH:
                try:
                    gathered_responses = asyncio.run(
                        self.process_batches(data_batches[start_idx:end_idx]),
                    )
                    for response in gathered_responses:
                        responses.append(
                            self._convert_historical_features_to_df(response),
                        )
                    break
                except Exception as e:
                    retry_count += 1
                    if retry_count == RETRY_PER_BATCH:
                        raise e
            progress_bar.update(end_idx - start_idx)

        # Concatenate the responses into a single DataFrame
        result_df = pd.concat(responses)
        progress_bar.close()

        def get_old_name(new_name: str) -> str:
            lower_case_name = new_name.lower()
            if lower_case_name in lower_case_column_to_old_column:
                return lower_case_column_to_old_column[lower_case_name]
            if lower_case_name in lower_case_feature_to_old_feature:
                return lower_case_feature_to_old_feature[lower_case_name]
            return new_name

        result_df = result_df.rename(columns=get_old_name)

        result_df[lower_case_column_to_old_column["timestamp"]] = pd.to_datetime(
            result_df[lower_case_column_to_old_column["timestamp"]],
        )

        return result_df.rename(columns=get_old_name)

    async def process_batches(self, batches: list[dict]) -> list[dict]:
        return await asyncio.gather(
            *[
                self._send_request_to_wyvern_api_async(
                    settings.WYVERN_HISTORICAL_FEATURES_PATH,
                    batch,
                )
                for batch in batches
            ],
        )

    def _send_request_to_wyvern_api(
        self,
        api_path: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{api_path}"
        response = requests.post(url, headers=self.headers, json=data)

        if response.status_code != 200:
            self._handle_failed_request(response)

        return response.json()

    async def _send_request_to_wyvern_api_async(
        self,
        api_path: str,
        data: Dict[str, Any],
    ) -> Dict[str, Any]:
        url = f"{self.base_url}{api_path}"
        response = await self.async_client.post(url, headers=self.headers, json=data)

        if response.status != 200:
            await self._handle_failed_async_request(response)

        return await response.json()

    def _handle_failed_request(
        self,
        response: requests.Response,
    ) -> None:
        raise WyvernError(f"Request failed [{response.status_code}]: {response.text}")

    async def _handle_failed_async_request(
        self,
        response: aiohttp.ClientResponse,
    ) -> None:
        text = await response.text()
        raise WyvernError(f"Request failed [{response.status}]: {text}")

    def _convert_online_features_to_df(
        self,
        data,
        get_event_timestamps: bool = False,
        get_feature_statuses: bool = False,
    ) -> pd.DataFrame:
        df_dict = {}
        feature_names = data["metadata"]["feature_names"]
        for i, feature in enumerate(feature_names):
            result = data["results"][i]
            df_dict[feature] = result["values"]
            if get_event_timestamps:
                df_dict[feature + "_event_timestamps"] = result["event_timestamps"]
            if get_feature_statuses:
                df_dict[feature + "_statuses"] = result["statuses"]

        return pd.DataFrame(df_dict)

    def _convert_historical_features_to_df(
        self,
        data,
    ) -> pd.DataFrame:
        df = pd.DataFrame(data["results"])
        return df
