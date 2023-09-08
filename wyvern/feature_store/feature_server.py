# -*- coding: utf-8 -*-
import importlib
import logging
import time
import traceback
from collections import defaultdict
from typing import Any, Dict, List, Tuple

import numpy as np
import pandas as pd
import uvicorn
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from feast import FeatureStore, proto_json
from feast.errors import EntityNotFoundException, FeatureViewNotFoundException
from feast.feature_store import _validate_entity_values, _validate_feature_refs
from feast.feature_view import (
    DUMMY_ENTITY,
    DUMMY_ENTITY_ID,
    DUMMY_ENTITY_NAME,
    DUMMY_ENTITY_VAL,
    FeatureView,
)
from feast.online_response import OnlineResponse
from feast.protos.feast.serving.ServingService_pb2 import GetOnlineFeaturesResponse
from feast.protos.feast.types.Value_pb2 import Value
from feast.type_map import python_values_to_proto_values
from feast.value_type import ValueType
from google.protobuf.json_format import MessageToDict

from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
)
from wyvern.config import settings
from wyvern.feature_store.historical_feature_util import (
    build_historical_real_time_feature_requests,
    build_historical_registry_feature_requests,
    process_historical_real_time_features_requests,
    process_historical_registry_features_requests,
    separate_real_time_features,
)
from wyvern.feature_store.schemas import (
    GetHistoricalFeaturesRequest,
    GetHistoricalFeaturesResponse,
    GetOnlineFeaturesRequest,
    MaterializeRequest,
)

logger = logging.getLogger(__name__)
CRONJOB_INTERVAL_SECONDS = 60 * 5  # 5 minutes
CRONJOB_LOOKBACK_MINUTES = 12  # 12 mins
MAX_HISTORICAL_REQUEST_SIZE = 16000


def _get_feature_views(
    features: List[str],
    all_feature_views: List[FeatureView],
) -> List[Tuple[FeatureView, List[str]]]:
    """
    Groups feature names by feature views.

    Arguments:
        features: List of feature references.
        all_feature_views: List of all feature views.

    Returns:
        List of tuples of feature views and feature names.
    """
    # view name to view proto
    view_index = {view.projection.name_to_use(): view for view in all_feature_views}

    # view name to feature names
    views_features = defaultdict(set)

    for ref in features:
        view_name, feat_name = ref.split(":")
        if view_name in view_index:
            view_index[view_name].projection.get_feature(feat_name)  # For validation
            views_features[view_name].add(feat_name)
        else:
            raise FeatureViewNotFoundException(view_name)

    fvs_result: List[Tuple[FeatureView, List[str]]] = []
    for view_name, feature_names in views_features.items():
        fvs_result.append((view_index[view_name], list(feature_names)))
    return fvs_result


def generate_wyvern_store_app(
    path: str,
) -> FastAPI:
    """
    Generate a FastAPI app for Wyvern feature store.

    Arguments:
        path: Path to the feature store repo.

    Returns:
        FastAPI app.
    """
    proto_json.patch()
    store = FeatureStore(repo_path=path)
    app = FastAPI()

    provider = store._get_provider()

    importlib.import_module(".main", "pipelines")

    @app.exception_handler(Exception)
    async def general_error_exception_handler(request: Request, exc: Exception):
        return JSONResponse(
            status_code=500,
            content={"error": str(exc)},
        )

    @app.middleware("http")
    async def request_middleware(request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        if request.url.path == "/healthcheck":
            return response
        process_time_ms = (time.time() - start_time) * 1000
        logger.info(
            f"process_time={process_time_ms} ms, "
            f"method={request.method}, url={request.url.path}, status_code={response.status_code}",
        )
        return response

    @app.get("/healthcheck")
    def healthcheck() -> Dict[str, str]:
        return {"status": "ok"}

    @app.post(settings.WYVERN_ONLINE_FEATURES_PATH)
    def get_online_features(data: GetOnlineFeaturesRequest) -> Dict[str, Any]:
        """
        Get online features from the feature store.

        Arguments:
            data: Request data. See schemas.py for the schema.

        Returns:
            Online features response.
        """
        try:
            # Validate and parse the request data into GetOnlineFeaturesRequest Protobuf object
            batch_sizes = [len(v) for v in data.entities.values()]
            num_entities = batch_sizes[0]
            if any(batch_size != num_entities for batch_size in batch_sizes):
                raise HTTPException(
                    status_code=500,
                    detail="Uneven number of columns",
                )
            _feature_refs = store._get_features(data.features, allow_cache=True)

            requested_feature_views = [
                *store._list_feature_views(True, False),
                *store._registry.list_stream_feature_views(
                    project=store.project,
                    allow_cache=True,
                ),
            ]

            (
                entity_name_to_join_key_map,
                entity_type_map,
                join_keys_set,
            ) = store._get_entity_maps(requested_feature_views)
            # Convert values to Protobuf once.
            entity_proto_values: Dict[str, List[Value]] = {
                k: python_values_to_proto_values(
                    v,
                    entity_type_map.get(k, ValueType.UNKNOWN),
                )
                for k, v in data.entities.items()
            }
            num_rows = _validate_entity_values(entity_proto_values)

            _validate_feature_refs(_feature_refs, data.full_feature_names)
            grouped_refs = _get_feature_views(
                _feature_refs,
                requested_feature_views,
            )
            # All requested features should be present in the result.
            requested_result_row_names = {
                feat_ref.replace(":", "__") for feat_ref in _feature_refs
            }
            if not data.full_feature_names:
                requested_result_row_names = {
                    name.rpartition("__")[-1] for name in requested_result_row_names
                }

            feature_views = list(view for view, _ in grouped_refs)

            join_key_values: Dict[str, List[Value]] = {}
            for join_key_or_entity_name, values in entity_proto_values.items():
                if join_key_or_entity_name in join_keys_set:
                    join_key = join_key_or_entity_name
                else:
                    try:
                        join_key = entity_name_to_join_key_map[join_key_or_entity_name]
                    except KeyError:
                        raise EntityNotFoundException(
                            join_key_or_entity_name,
                            store.project,
                        )
                    else:
                        logger.warning(
                            "Using entity name is deprecated. Use join_key instead.",
                        )

                # All join keys should be returned in the result.
                requested_result_row_names.add(join_key)
                join_key_values[join_key] = values

            # Populate online features response proto with join keys and request data features
            online_features_response = GetOnlineFeaturesResponse(results=[])
            store._populate_result_rows_from_columnar(
                online_features_response=online_features_response,
                data=dict(**join_key_values),
            )

            # Add the Entityless case after populating result rows to avoid having to remove
            # it later.
            entityless_case = DUMMY_ENTITY_NAME in [
                entity_name
                for feature_view in feature_views
                for entity_name in feature_view.entities
            ]
            if entityless_case:
                join_key_values[DUMMY_ENTITY_ID] = python_values_to_proto_values(
                    [DUMMY_ENTITY_VAL] * num_rows,
                    DUMMY_ENTITY.value_type,
                )

            for table, requested_features in grouped_refs:
                # Get the correct set of entity values with the correct join keys.
                table_entity_values, idxs = store._get_unique_entities(
                    table,
                    join_key_values,
                    entity_name_to_join_key_map,
                )

                # Fetch feature data for the minimum set of Entities.
                feature_data = store._read_from_online_store(
                    table_entity_values,
                    provider,
                    requested_features,
                    table,
                )

                # Populate the result_rows with the Features from the OnlineStore inplace.
                store._populate_response_from_feature_data(
                    feature_data,
                    idxs,
                    online_features_response,
                    data.full_feature_names,
                    requested_features,
                    table,
                )
            store._drop_unneeded_columns(
                online_features_response,
                requested_result_row_names,
            )
            response_proto = OnlineResponse(online_features_response).proto

            # Convert the Protobuf object to JSON and return it
            result = MessageToDict(  # type: ignore
                response_proto,
                preserving_proto_field_name=True,
                float_precision=18,
            )
            return result
        except Exception as e:
            # Print the original exception on the server side
            logger.exception(traceback.format_exc())
            # Raise HTTPException to return the error message to the client
            raise HTTPException(status_code=500, detail=str(e))

    @app.post("/feature/materialize", status_code=201)
    async def materialize(data: MaterializeRequest) -> None:
        """
        Materialize the feature store and refresh the registry. This is a blocking call.

        Arguments:
            data: Request data. See schemas.py for the schema.

        Returns:
            None.
        """
        try:
            logger.info(f"materialize called: {data}")
            if data.start_date:
                # materialize from start to end
                store.materialize(
                    start_date=data.start_date,
                    end_date=data.end_date,
                    feature_views=data.feature_views,
                )
            else:
                store.materialize_incremental(
                    end_date=data.end_date,
                    feature_views=data.feature_views,
                )
            store.refresh_registry()
            logger.info("registry refreshed")
        except Exception as e:
            logger.exception(traceback.format_exc())
            raise HTTPException(status_code=500, detail=str(e))

    @app.post(settings.WYVERN_HISTORICAL_FEATURES_PATH)
    async def get_historical_features(
        data: GetHistoricalFeaturesRequest,
    ) -> GetHistoricalFeaturesResponse:
        """
        Wyvern feature store's historical features include realtime historical feature logged by wyvern pipeline and
            offline historical features.

        Currently, we use the feast's offline features and support historical realtime features only on snowflake.

        Arguments:
            data: Request data. See schemas.py for the schema.

            data.entities: entities must contain two required columns, request and timestamp.
                Besides the required columns, it contains all the entity columns (product, query, etc.),
                as well as the extra feature data columns (like is_purchased, is_clicked, etc.).

        Returns:
            Historical features response.
        """
        # validate the data input: lengths of requests, timestamps and all the entities should be the same
        if "request" not in data.entities:
            raise HTTPException(
                status_code=400,
                detail="request is required in entities",
            )
        length_of_requests = len(data.entities["request"])
        length_of_timestamps = len(data.timestamps)
        if length_of_requests != length_of_timestamps:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"Length of requests({length_of_requests}) and "
                    f"timestamps({length_of_timestamps}) should be the same"
                ),
            )
        if length_of_requests > MAX_HISTORICAL_REQUEST_SIZE:
            raise HTTPException(
                status_code=400,
                detail=(
                    f"The max size of requests is {MAX_HISTORICAL_REQUEST_SIZE}. Got {length_of_requests} requests."
                ),
            )
        for key, value in data.entities.items():
            if len(value) != length_of_requests:
                raise HTTPException(
                    status_code=400,
                    detail=f"Length of requests({length_of_requests}) and {key}({len(value)}) should be the same",
                )

        # convert the data input to pandas dataframe
        data.entities["timestamp"] = data.timestamps
        df = pd.DataFrame(data.entities)
        realtime_features, feast_features = separate_real_time_features(data.features)
        # TODO: analyze all the realtime features and generate all the composite feature columns in the dataframe
        # the column name will be the composite feature name
        valid_realtime_features: List[str] = []
        composite_entities: Dict[str, List[str]] = {}
        for realtime_feature in realtime_features:
            entity_type_column = RealtimeFeatureComponent.get_entity_type_column(
                realtime_feature,
            )
            entity_names = RealtimeFeatureComponent.get_entity_names(realtime_feature)
            if not entity_type_column or not entity_names:
                logger.warning(f"feature={realtime_feature} is not found")
                continue

            if len(entity_names) == 2:
                entity_name_1 = entity_names[0]
                entity_name_2 = entity_names[1]
                if entity_name_1 not in data.entities:
                    logger.warning(
                        f"Realtime feature {realtime_feature} depends on "
                        f"entity={entity_name_1}, which is not found in entities",
                    )
                    continue
                if entity_name_2 not in data.entities:
                    logger.warning(
                        f"Realtime feature {realtime_feature} depends on "
                        f"entity={entity_name_2}, which is not found in entities",
                    )
                    continue
                composite_entities[entity_type_column] = entity_names
            valid_realtime_features.append(realtime_feature)

        # TODO: generate all the composite feature columns in the dataframe
        for entity_type_column in composite_entities:
            entity_name1, entity_name2 = composite_entities[entity_type_column]
            df[entity_type_column] = df[entity_name1] + ":" + df[entity_name2]

        realtime_requests = build_historical_real_time_feature_requests(
            full_feature_names=valid_realtime_features,
            request_ids=data.entities["request"],
            entities=data.entities,
        )

        real_time_responses = process_historical_real_time_features_requests(
            requests=realtime_requests,
        )
        for entity_identifier_type, features_df in real_time_responses.items():
            df = df.merge(
                features_df,
                left_on=["request", entity_identifier_type],
                right_on=["REQUEST_ID", entity_identifier_type.upper()],
                how="left",
            )
            df.drop(columns=["REQUEST_ID"], inplace=True)

        feast_requests = build_historical_registry_feature_requests(
            store=store,
            feature_names=feast_features,
            entity_values=data.entities,
            timestamps=data.timestamps,
        )
        feast_responses = process_historical_registry_features_requests(
            store=store,
            requests=feast_requests,
        )

        for feast_response in feast_responses:
            if len(feast_response.IDENTIFIER) != len(df["request"]):
                raise HTTPException(
                    status_code=400,
                    detail=(
                        f"Length of feature store response({len(feast_response.IDENTIFIER)}) "
                        f"and request({len(df['request'])}) should be the same"
                    ),
                )
            new_columns = [
                column
                for column in feast_response.columns
                if column not in ["IDENTIFIER", "event_timestamp"]
            ]
            df = df.join(feast_response[new_columns])

        composite_keys = [key for key in composite_entities.keys() if key in df]
        composite_keys_uppercase = [
            key.upper() for key in composite_entities.keys() if key.upper() in df
        ]
        drop_columns = composite_keys + composite_keys_uppercase + ["REQUEST_ID"]
        drop_columns = [column for column in drop_columns if column in df]
        df.drop(columns=drop_columns, inplace=True)
        final_df = df.replace({np.nan: None})
        final_df["timestamp"] = final_df["timestamp"].astype(str)

        return GetHistoricalFeaturesResponse(
            results=final_df.to_dict(orient="records"),
        )

    return app


def start_wyvern_store(
    path: str,
    host: str,
    port: int,
):
    """
    Start the Wyvern feature store.

    Arguments:
        path: Path to the feature store repo.
        host: Host to run the feature store on.
        port: Port to run the feature store on.
    """
    app = generate_wyvern_store_app(path)
    uvicorn.run(
        app,
        host=host,
        port=port,
        timeout_keep_alive=settings.FEATURE_STORE_TIMEOUT,
    )
