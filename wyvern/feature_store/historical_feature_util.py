# -*- coding: utf-8 -*-
import logging
import re
from collections import defaultdict
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

import more_itertools
import pandas as pd
from feast import FeatureStore
from snowflake.connector import SnowflakeConnection

from wyvern.clients.snowflake import generate_snowflake_ctx
from wyvern.components.features.realtime_features_component import (
    RealtimeFeatureComponent,
)
from wyvern.config import settings
from wyvern.exceptions import EntityColumnMissingError
from wyvern.feature_store.constants import (
    FULL_FEATURE_NAME_SEPARATOR,
    SQL_COLUMN_SEPARATOR,
)
from wyvern.feature_store.schemas import (
    GetFeastHistoricalFeaturesRequest,
    RequestEntityIdentifierObjects,
)

logger = logging.getLogger(__name__)


def separate_real_time_features(
    full_feature_names: Optional[List[str]],
) -> Tuple[List[str], List[str]]:
    """
    Given a list of full feature names, separate real-time features and other features.

    Args:
        full_feature_names: a list of full feature names.

    Returns:
        Real time feature names and other feature names in two lists respectively.
    """
    if full_feature_names is None:
        return [], []

    f_is_real_time_feature = (
        lambda feature: RealtimeFeatureComponent.get_entity_type_column(feature)
        is not None
    )
    other_feature_names, real_time_feature_names = more_itertools.partition(
        f_is_real_time_feature,
        full_feature_names,
    )
    logger.debug(f"real_time_feature_names: {real_time_feature_names}")
    logger.debug(f"other_feature_names: {other_feature_names}")
    return list(real_time_feature_names), list(other_feature_names)


def build_historical_real_time_feature_requests(
    full_feature_names: List[str],
    request_ids: List[str],
    entities: Dict[str, List[Any]],
) -> Dict[str, RequestEntityIdentifierObjects]:
    """
    Build historical real-time feature requests grouped by entity types so that we can process them in parallel.

    Args:
        full_feature_names: a list of full feature names.
        request_ids: a list of request ids.
        entities: a dictionary of entity names and their values.

    Returns:
        A dictionary of entity types and their corresponding requests.
    """
    features_grouped_by_entity = group_realtime_features_by_entity_type(
        full_feature_names=full_feature_names,
    )
    request_length = len(request_ids)
    for feature_name, feature_identifiers in entities.items():
        if len(feature_identifiers) != request_length:
            raise ValueError(
                f"Number of {feature_name} features ({len(feature_identifiers)}) "
                f"does not match number of requests ({request_length})",
            )
    result_dict: Dict[str, RequestEntityIdentifierObjects] = {}
    for (
        entity_identifier_type,
        curr_feature_names,
    ) in features_grouped_by_entity.items():
        entity_list = entity_identifier_type.split(SQL_COLUMN_SEPARATOR)

        # validate entity_list
        for entity in entity_list:
            if entity not in entities:
                raise EntityColumnMissingError(entity=entity)

        if len(entity_list) > 2:
            return result_dict

        if len(entity_list) == 1:
            # could just get all the entity_identifiers from the entities dict right away
            result_dict[entity_identifier_type] = RequestEntityIdentifierObjects(
                request_ids=request_ids,
                entity_identifiers=entities[entity_identifier_type],
                feature_names=curr_feature_names,
            )
        elif len(entity_list) == 2:
            # need to combine the entity_identifiers from the entities dict
            list1 = entities[entity_list[0]]
            list2 = entities[entity_list[1]]
            result_dict[entity_identifier_type] = RequestEntityIdentifierObjects(
                request_ids=request_ids,
                entity_identifiers=[
                    f"{list1[idx]}:{list2[idx]}" for idx in range(len(list1))
                ],
                feature_names=curr_feature_names,
            )
    return result_dict


def build_and_merge_realtime_pivot_tables(
    full_feature_names: List[str],
    input_table: str,
    composite_table: str,
    context: SnowflakeConnection,
) -> str:
    """
    Build historical real-time feature requests grouped by entity types so that we can process them in parallel.

    Args:
        full_feature_names: a list of full feature names.
        request_ids: a list of request ids.
        entities: a dictionary of entity names and their values.

    Returns:
        A dictionary of entity types and their corresponding requests.
    """
    features_grouped_by_entity = group_realtime_features_by_entity_type(
        full_feature_names=full_feature_names,
    )
    counter = 0

    # prev_table is the previous temporary composite table
    prev_table = composite_table
    # next_table is the next temporary composite table joined with the next entity type
    next_table = f"{composite_table}_0"

    # iterate through all the entity types.
    # For each entity type, build a new temporary composite table with all the features for this entity type
    for (
        entity_identifier_type,
        curr_feature_names,
    ) in features_grouped_by_entity.items():
        entity_list = entity_identifier_type.split(SQL_COLUMN_SEPARATOR)

        if len(entity_list) > 2:
            logger.warning("Invalid entity_identifier_type={entity_identifier_type}")
            continue
        curr_feature_names_underscore = [
            fn.replace(":", "__", 1) for fn in curr_feature_names
        ]
        entity_identifier_type_val = ":".join(entity_list)
        feature_names_sql_str = ",".join(
            [f"'{fn}'" for fn in curr_feature_names_underscore],
        )
        feature_names_with_pivot_table_str = ",".join(
            [
                f"PIVOT_TABLE.{feature_name}"
                for feature_name in curr_feature_names_underscore
            ],
        )
        feature_names_pivot_raw = ",".join(
            [f"\"'{fn}'\" as {fn}" for fn in curr_feature_names_underscore],
        )

        # TODO: send this sql to snowflake
        pivot_sql = f"""
        CREATE TEMPORARY TABLE {next_table} AS (
            WITH PIVOT_DATA AS (
                SELECT F.REQUEST_ID AS REQUEST,
                       F.API_SOURCE,
                       F.EVENT_TYPE,
                       F.FEATURE_IDENTIFIER,
                       F.FEATURE_IDENTIFIER_TYPE,
                       REPLACE(F.FEATURE_NAME, ':', '__') AS FEATURE_NAME,
                       F.FEATURE_VALUE
                FROM FEATURE_LOGS F
                INNER JOIN (SELECT DISTINCT REQUEST FROM {input_table}) T
                ON F.REQUEST_ID = T.REQUEST
                WHERE F.FEATURE_IDENTIFIER_TYPE = '{entity_identifier_type_val}'
            ), PIVOT_TABLE_RAW AS (
                SELECT *
                FROM PIVOT_DATA
                PIVOT(MAX(FEATURE_VALUE) FOR FEATURE_NAME IN ({feature_names_sql_str}))
            ), PIVOT_TABLE AS (
                SELECT REQUEST, FEATURE_IDENTIFIER, FEATURE_IDENTIFIER_TYPE, {feature_names_pivot_raw}
                FROM PIVOT_TABLE_RAW
            )
            SELECT
                {prev_table}.*,{feature_names_with_pivot_table_str}
            FROM
                {prev_table}
            LEFT JOIN PIVOT_TABLE ON
                {prev_table}.REQUEST = PIVOT_TABLE.REQUEST AND
                {prev_table}.{entity_identifier_type} = PIVOT_TABLE.FEATURE_IDENTIFIER
        )
        """
        context.cursor().execute(pivot_sql)
        counter += 1
        prev_table = next_table
        next_table = f"{composite_table}_{counter}"
    return prev_table


def process_historical_real_time_features_requests(
    requests: Dict[str, RequestEntityIdentifierObjects],
) -> Dict[str, pd.DataFrame]:
    """
    Given a dictionary of historical real-time feature requests, process them and return the results.

    Args:
        requests: a dictionary of entity types and their corresponding requests.

    Returns:
        A dictionary of entity types and their corresponding results in pandas dataframes.
    """
    result: Dict[str, pd.DataFrame] = {}
    with generate_snowflake_ctx() as context:
        for entity_identifier_type, request in requests.items():
            result[
                entity_identifier_type
            ] = process_historical_real_time_features_request(
                entity_identifier_type=entity_identifier_type,
                request=request,
                context=context,
            )
    return result


def process_historical_real_time_features_request(
    entity_identifier_type: str,
    request: RequestEntityIdentifierObjects,
    context: SnowflakeConnection,
) -> pd.DataFrame:
    """
    Given a historical real-time feature request, process it and return the results.

    Args:
        entity_identifier_type: the entity type of the request. E.g. "product__query"
        request: the request object.
        context: the snowflake connection context.

    Returns:
        The result in pandas dataframe.
    """
    case_when_statements = [
        f"MAX(CASE WHEN FEATURE_NAME = '{feature_name}' THEN FEATURE_VALUE END) AS {feature_name.replace(':', '__')}"
        for feature_name in request.feature_names
    ]
    # TODO (shu): the table name FEATURE_LOGS_PROD is hard-coded right now. Make this configurable or an env var.
    query = f"""
    SELECT
        REQUEST_ID,
        FEATURE_IDENTIFIER AS {entity_identifier_type},
        {",".join(case_when_statements)}
    from {settings.SNOWFLAKE_REALTIME_FEATURE_LOG_TABLE}
    where
        REQUEST_ID in ({','.join(['%s'] * len(request.request_ids))}) and
        FEATURE_IDENTIFIER in ({','.join(['%s'] * len(request.entity_identifiers))})
    group by 1, 2
    """
    with context.cursor() as cursor:
        # entity_identifiers is a list of strings as the parameters for the query
        cursor.execute(query, request.request_ids + request.entity_identifiers)
        return cursor.fetch_pandas_all()


def group_realtime_features_by_entity_type(
    full_feature_names: List[str],
) -> Dict[str, List[str]]:
    """
    Given a list of feature names, group them by their entity_identifier_type

    Args:
        full_feature_names: a list of full feature names.

    Returns:
        A dictionary of entity types and their corresponding feature names.
    """
    feature_entity_mapping: Dict[str, str] = {}
    for full_feature_name in full_feature_names:

        # we want to use the column name which is using the separator __
        # because no ":" is allowed in the column name
        entity_identifier_type = RealtimeFeatureComponent.get_entity_type_column(
            full_feature_name,
        )

        if entity_identifier_type is None:
            logger.warning(f"Could not find entity for feature: {full_feature_name}")
            continue
        feature_entity_mapping[full_feature_name] = entity_identifier_type

    logger.debug(f"feature_entity_mapping: {feature_entity_mapping}")
    entity_feature_mapping: Dict[str, List[str]] = defaultdict(list)
    for feature, entity_identifier_type in feature_entity_mapping.items():
        entity_feature_mapping[entity_identifier_type].append(feature)
    logger.debug(f"entity_feature_mapping: {entity_feature_mapping}")
    return entity_feature_mapping


def group_registry_features_by_entities(
    full_feature_names: List[str],
    store: FeatureStore,
) -> Dict[str, List[str]]:
    """
    Given a list of feature names, group them by their entity name.

    Args:
        full_feature_names: a list of full feature names.
        store: the feast feature store.

    Returns:
        A dictionary of entity names and their corresponding feature names.
    """
    entity_feature_mapping: Dict[str, List[str]] = defaultdict(list)

    # Precompute registry feature views and entity name mapping
    fvs = store.registry.list_feature_views(project=store.project)

    for fv in fvs:
        if len(fv.entities) > 1:
            raise ValueError(
                f"Feature view {fv.name} has more than one entity, which is not supported yet",
            )
        entity_name = fv.entities[0].lower()
        entity_feature_mapping[entity_name].extend(
            feature_name
            for feature_name in full_feature_names
            if feature_name.startswith(f"{fv.name}:")
        )

    return entity_feature_mapping


def build_historical_registry_feature_requests(
    store: FeatureStore,
    feature_names: List[str],
    entity_values: Dict[str, List[Any]],
    timestamps: List[datetime],
) -> List[GetFeastHistoricalFeaturesRequest]:
    """
    Build historical feature requests grouped by entity names so that we can process them in parallel.

    Args:
        store: the feast feature store.
        feature_names: a list of feature names.
        entity_values: a dictionary of entity names and their values.
        timestamps: a list of timestamps for getting historical features at those timestamps.

    Returns:
        A list of historical feature requests.
    """
    features_grouped_by_entities = group_registry_features_by_entities(
        feature_names,
        store=store,
    )
    requests: List[GetFeastHistoricalFeaturesRequest] = []
    for entity_name, feature_names in features_grouped_by_entities.items():
        if not feature_names:
            continue

        if FULL_FEATURE_NAME_SEPARATOR in entity_name:
            entities = entity_name.split(FULL_FEATURE_NAME_SEPARATOR)
        else:
            entities = [entity_name]

        if len(entities) > 2:
            raise ValueError(
                f"Entity name should be singular or composite: {entity_name}",
            )
        for entity in entities:
            if entity not in entity_values:
                raise ValueError(
                    f"{feature_names} depends on {entity}. Could not find entity values: {entity}",
                )
        request_entities: Dict[str, List[Any]]
        if len(entities) == 1:
            request_entities = {
                "IDENTIFIER": [str(v) for v in entity_values[entities[0]]],
            }
        else:
            list1 = entity_values[entities[0]]
            list2 = entity_values[entities[1]]

            request_entities = {
                "IDENTIFIER": [
                    f"{list1[idx]:{list2[idx]}}" for idx in range(len(list1))
                ],
            }
        request_entities["event_timestamp"] = timestamps

        requests.append(
            GetFeastHistoricalFeaturesRequest(
                features=feature_names,
                entities=request_entities,
                full_feature_names=True,
            ),
        )

    return requests


def build_and_merge_feast_tables(
    store: FeatureStore,
    feature_names: List[str],
    composite_table: str,
    context: SnowflakeConnection,
) -> str:
    features_grouped_by_entities = group_registry_features_by_entities(
        feature_names,
        store=store,
    )
    counter = 0
    prev_table = composite_table
    next_table = f"{composite_table}_0"
    for entity_name, feature_names in features_grouped_by_entities.items():
        if not feature_names:
            continue

        if FULL_FEATURE_NAME_SEPARATOR in entity_name:
            entities = entity_name.split(FULL_FEATURE_NAME_SEPARATOR)
        else:
            entities = [entity_name]

        if len(entities) > 2:
            raise ValueError(
                f"Entity name should be singular or composite: {entity_name}",
            )

        feature_columns = [fn.replace(":", "__") for fn in feature_names]

        # TODO: validate that all entities are in the entity_df_table
        # for entity in entities:
        # if entity not in entity_values:
        #     raise ValueError(
        #         f"{feature_names} depends on {entity}. Could not find entity values: {entity}",
        #     )
        identifier_column = SQL_COLUMN_SEPARATOR.join(entities)
        identifier_table_sql_dupe = f"""
        SELECT
            {identifier_column} AS IDENTIFIER,
            event_timestamp,
            ROW_NUMBER() OVER (PARTITION BY IDENTIFIER, event_timestamp ORDER BY (SELECT NULL)) as rn
        FROM {composite_table}
        WHERE {identifier_column} is NOT NULL
        """

        # dedupe (IDENTIFIER, event_timestamp)
        identifier_table_sql = f"""
        WITH identifier_table_sql_dupe AS ({identifier_table_sql_dupe})
        SELECT IDENTIFIER, event_timestamp
        FROM identifier_table_sql_dupe
        WHERE rn = 1
        """
        result = store.get_historical_features(
            entity_df=identifier_table_sql,
            features=feature_names or [],
            full_feature_names=True,
        )
        result_sql = result.to_sql()
        # Strip the leading "WITH " (WITH plus an empty space)
        result_sql = result_sql.replace("WITH ", "")
        # Replace the table name with 'identifier_tbl', assuming the table name is always
        # in the format "feast_entity_df_" followed by a hex string (UUID without dashes)
        result_sql = re.sub(
            r'"feast_entity_df_[0-9a-f]{32}"',
            "identifier_tbl",
            result_sql,
            flags=re.IGNORECASE,
        )
        new_feast_table_sql = f"""
        CREATE TEMPORARY TABLE {next_table}_feast AS (
        WITH identifier_tbl_dupe AS ({identifier_table_sql_dupe}),
        identifier_tbl AS (
            SELECT IDENTIFIER, event_timestamp
            FROM identifier_tbl_dupe
            WHERE rn = 1
        ),
            {result_sql}
        )
        """
        context.cursor().execute(new_feast_table_sql)

        # left join to the previous composite table
        picked_feature_columns_str = ", ".join(
            [f'{next_table}_feast."{c}"' for c in feature_columns],
        )
        new_composite_table_sql = f"""
        CREATE TABLE {next_table} AS (
            SELECT {prev_table}.*, {picked_feature_columns_str}
            FROM {prev_table}
            LEFT JOIN {next_table}_feast
            ON {prev_table}.{identifier_column} = {next_table}_feast.IDENTIFIER and
                {prev_table}.event_timestamp = {next_table}_feast.event_timestamp
        )
        """
        context.cursor().execute(new_composite_table_sql)

        counter += 1
        prev_table = next_table
        next_table = f"{composite_table}_{counter}"

    return prev_table


def process_historical_registry_features_requests(
    store: FeatureStore,
    requests: List[GetFeastHistoricalFeaturesRequest],
) -> List[pd.DataFrame]:
    """
    Given a list of historical feature requests, process them and return the results

    Args:
        store: the feast feature store.
        requests: a list of historical feature requests.

    Returns:
        A list of results in pandas dataframes.
    """
    results = []
    for request in requests:
        result = process_historical_registry_features_request(store, request)
        results.append(result)
    return results


def process_historical_registry_features_request(
    store: FeatureStore,
    request: GetFeastHistoricalFeaturesRequest,
) -> pd.DataFrame:
    """
    Given a historical feature request, process it and return the results

    Args:
        store: the feast feature store.
        request: a historical feature request.

    Returns:
        The result in pandas dataframe.
    """
    entity_df = pd.DataFrame(request.entities)
    # no timezone is allowed in the timestamp
    entity_df["event_timestamp"] = entity_df["event_timestamp"].dt.tz_localize(None)
    # TODO: use sql to get the result.
    # example:
    # https://docs.feast.dev/getting-started/concepts/feature-retrieval
    # #example-entity-sql-query-for-generating-training-data
    result = store.get_historical_features(
        entity_df=entity_df,
        features=request.features or [],
        full_feature_names=request.full_feature_names,
    )
    # TODO: to_sql(); replace IDENTIFIER by the original identifier_type
    result_df = result.to_df()
    # TODO: group IDENTIFIER and event_timestamp
    result_df.drop_duplicates(subset=["IDENTIFIER", "event_timestamp"], inplace=True)
    return entity_df.merge(
        result_df,
        on=["IDENTIFIER", "event_timestamp"],
        how="left",
    )
