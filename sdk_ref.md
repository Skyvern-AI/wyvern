<a id="wyvern"></a>

# wyvern

<a id="wyvern.clients"></a>

# wyvern.clients

<a id="wyvern.clients.snowflake"></a>

# wyvern.clients.snowflake

<a id="wyvern.clients.snowflake.generate_snowflake_ctx"></a>

#### generate_snowflake_ctx

```python
def generate_snowflake_ctx() -> snowflake.connector.SnowflakeConnection
```

Generate a Snowflake context from the settings

<a id="wyvern.service"></a>

# wyvern.service

<a id="wyvern.service.WyvernService"></a>

## WyvernService Objects

```python
class WyvernService()
```

The class to define, generate and run a Wyvern service

**Attributes**:

- `host` - The host to run the service on. Defaults to localhost.
- `port` - The port to run the service on. Defaults to 5000.

<a id="wyvern.service.WyvernService.register_routes"></a>

#### register_routes

```python
async def register_routes(
        route_components: List[Type[APIRouteComponent]]) -> None
```

Register the routes for the Wyvern service

**Arguments**:

- `route_components` - The list of route components to register

**Returns**:

None

<a id="wyvern.service.WyvernService.generate"></a>

#### generate

```python
@staticmethod
def generate(*,
             route_components: Optional[List[Type[APIRouteComponent]]] = None,
             realtime_feature_components: Optional[List[
                 Type[RealtimeFeatureComponent]]] = None,
             host: str = "127.0.0.1",
             port: int = 5000) -> WyvernService
```

Generate a Wyvern service

**Arguments**:

- `route_components` - The list of route components to register. Defaults to None.
- `realtime_feature_components` - The list of realtime feature components to register. Defaults to None.
- `host` - The host to run the service on. Defaults to localhost.
- `port` - The port to run the service on. Defaults to 5000.

**Returns**:

- `WyvernService` - The generated Wyvern service

<a id="wyvern.service.WyvernService.run"></a>

#### run

```python
@staticmethod
def run(*,
        route_components: List[Type[APIRouteComponent]],
        realtime_feature_components: Optional[List[
            Type[RealtimeFeatureComponent]]] = None,
        host: str = "127.0.0.1",
        port: int = 5000)
```

Generate and run a Wyvern service

**Arguments**:

- `route_components` - The list of route components to register
- `realtime_feature_components` - The list of realtime feature components to register. Defaults to None.
- `host` - The host to run the service on. Defaults to localhost.
- `port` - The port to run the service on. Defaults to 5000.

**Returns**:

None

<a id="wyvern.service.WyvernService.generate_app"></a>

#### generate_app

```python
@staticmethod
def generate_app(*,
                 route_components: Optional[List[
                     Type[APIRouteComponent]]] = None,
                 realtime_feature_components: Optional[List[
                     Type[RealtimeFeatureComponent]]] = None,
                 host: str = "127.0.0.1",
                 port: int = 5000) -> FastAPI
```

Generate a Wyvern service and return the FastAPI app

**Arguments**:

- `route_components` - The list of route components to register. Defaults to None.
- `realtime_feature_components` - The list of realtime feature components to register. Defaults to None.
- `host` _str, optional_ - The host to run the service on. Defaults to localhost.
- `port` _int, optional_ - The port to run the service on. Defaults to 5000.

**Returns**:

- `FastAPI` - The generated FastAPI app

<a id="wyvern.config"></a>

# wyvern.config

<a id="wyvern.config.Settings"></a>

## Settings Objects

```python
class Settings(BaseSettings)
```

Settings for the Wyvern service

Extends from BaseSettings class, allowing values to be overridden by environment variables. This is useful
in production for secrets you do not wish to save in code

**Attributes**:

- `ENVIRONMENT` - The environment the service is running in.
- `PROJECT_NAME` - The name of the project
- `REDIS_HOST` - The host of the redis instance
- `REDIS_PORT` - The port of the redis instance

- `WYVERN_API_KEY` - The API key for the Wyvern API
- `WYVERN_BASE_URL` - The base url of the Wyvern API
- `WYVERN_ONLINE_FEATURES_PATH` - The path to the online features endpoint
- `WYVERN_HISTORICAL_FEATURES_PATH` - The path to the historical features endpoint
- `WYVERN_FEATURE_STORE_URL` - The url of the Wyvern feature store

- `SNOWFLAKE_ACCOUNT` - The account name of the Snowflake instance
- `SNOWFLAKE_USER` - The username of the Snowflake instance
- `SNOWFLAKE_PASSWORD` - The password of the Snowflake instance
- `SNOWFLAKE_ROLE` - The role of the Snowflake instance
- `SNOWFLAKE_WAREHOUSE` - The warehouse of the Snowflake instance
- `SNOWFLAKE_DATABASE` - The database of the Snowflake instance
- `SNOWFLAKE_OFFLINE_STORE_SCHEMA` - The schema of the Snowflake instance

- `AWS_ACCESS_KEY_ID` - The access key id for the AWS instance
- `AWS_SECRET_ACCESS_KEY` - The secret access key for the AWS instance
- `AWS_REGION_NAME` - The region name for the AWS instance

- `FEATURE_STORE_TIMEOUT` - The timeout for the feature store
- `SERVER_TIMEOUT` - The timeout for the server

- `REDIS_BATCH_SIZE` - The batch size for the redis instance
- `WYVERN_INDEX_VERSION` - The version of the Wyvern index
- `MODELBIT_BATCH_SIZE` - The batch size for the modelbit

- `EXPERIMENTATION_ENABLED` - Whether experimentation is enabled
- `EXPERIMENTATION_PROVIDER` - The experimentation provider
- `EPPO_API_KEY` - The API key for EPPO (an experimentation provider)

- `FEATURE_STORE_ENABLED` - Whether the feature store is enabled
- `EVENT_LOGGING_ENABLED` - Whether event logging is enabled

<a id="wyvern.core.compression"></a>

# wyvern.core.compression

<a id="wyvern.core.compression.wyvern_encode"></a>

#### wyvern_encode

```python
def wyvern_encode(data: Dict[str, Any]) -> bytes
```

encode a dict to compressed bytes using lz4.frame

<a id="wyvern.core.compression.wyvern_decode"></a>

#### wyvern_decode

```python
def wyvern_decode(data: Union[bytes, str]) -> Dict[str, Any]
```

decode compressed bytes to a dict with lz4.frame

<a id="wyvern.core"></a>

# wyvern.core

<a id="wyvern.core.http"></a>

# wyvern.core.http

<a id="wyvern.core.http.AiohttpClientWrapper"></a>

## AiohttpClientWrapper Objects

```python
class AiohttpClientWrapper()
```

AiohttpClientWrapper is a singleton wrapper around aiohttp.ClientSession.

<a id="wyvern.core.http.AiohttpClientWrapper.start"></a>

#### start

```python
def start()
```

Instantiate the client. Call from the FastAPI startup hook.

<a id="wyvern.core.http.AiohttpClientWrapper.stop"></a>

#### stop

```python
async def stop()
```

Gracefully shutdown. Call from FastAPI shutdown hook.

<a id="wyvern.core.http.AiohttpClientWrapper.__call__"></a>

#### \_\_call\_\_

```python
def __call__()
```

Calling the instantiated AiohttpClientWrapper returns the wrapped singleton.

<a id="wyvern.core.http.aiohttp_client"></a>

#### aiohttp_client

The aiohttp client singleton. Use this to make requests.

**Example**:

    ```python
    from wyvern.core.http import aiohttp_client
    aiohttp_client().get("https://www.wyvern.ai")
    ```

<a id="wyvern.experimentation.experimentation_logging"></a>

# wyvern.experimentation.experimentation_logging

<a id="wyvern.experimentation.experimentation_logging.ExperimentationEventData"></a>

## ExperimentationEventData Objects

```python
class ExperimentationEventData(BaseModel)
```

Data class for ExperimentationEvent.

**Attributes**:

- `experiment_id` - The experiment id.
- `entity_id` - The entity id.
- `result` - The result of the experiment. Can be None.
- `timestamp` - The timestamp of the event.
- `metadata` - The metadata of the event such as targeting parameters etc.
- `has_error` - Whether the request has errored or not.

<a id="wyvern.experimentation.experimentation_logging.ExperimentationEvent"></a>

## ExperimentationEvent Objects

```python
class ExperimentationEvent(LoggedEvent[ExperimentationEventData])
```

Event class for ExperimentationEvent.

**Attributes**:

- `event_type` - The event type. This is always EventType.EXPERIMENTATION.

<a id="wyvern.experimentation.providers"></a>

# wyvern.experimentation.providers

<a id="wyvern.experimentation.providers.eppo_provider"></a>

# wyvern.experimentation.providers.eppo_provider

<a id="wyvern.experimentation.providers.eppo_provider.EppoExperimentationClient"></a>

## EppoExperimentationClient Objects

```python
class EppoExperimentationClient(BaseExperimentationProvider)
```

An experimentation client specifically for the Eppo platform.

Extends the BaseExperimentationProvider to provide functionality using the Eppo client.

**Methods**:

- **init**() -> None
- get_result(experiment_id: str, entity_id: str, \*\*kwargs) -> str
- log_result(experiment_id: str, entity_id: str, variant: str) -> None

<a id="wyvern.experimentation.providers.eppo_provider.EppoExperimentationClient.get_result"></a>

#### get_result

```python
def get_result(experiment_id: str, entity_id: str, **kwargs) -> str
```

Fetches the variant for a given experiment and entity from the Eppo client.

**Arguments**:

- experiment_id (str): The unique ID of the experiment.
- entity_id (str): The unique ID of the entity (e.g., user or other subject).
- \*\*kwargs: Additional arguments to be passed to the Eppo client's get_assignment method.

**Returns**:

- str: The assigned variant for the given experiment and entity.

<a id="wyvern.experimentation.providers.eppo_provider.EppoExperimentationClient.log_result"></a>

#### log_result

```python
def log_result(experiment_id: str,
               entity_id: str,
               variant: Optional[str] = None,
               has_error: bool = False,
               **kwargs) -> None
```

Logs the result for a given experiment and entity.

**Arguments**:

- experiment_id (str): The unique ID of the experiment.
- entity_id (str): The unique ID of the entity.
- variant (str): The assigned variant for the given experiment and entity.

- `Note` - This method is overridden to do nothing because the assignment logger we set in Eppo already
  handles result logging upon assignment.

<a id="wyvern.experimentation.providers.base"></a>

# wyvern.experimentation.providers.base

<a id="wyvern.experimentation.providers.base.ExperimentationProvider"></a>

## ExperimentationProvider Objects

```python
class ExperimentationProvider(str, Enum)
```

An enum for the experimentation providers.

<a id="wyvern.experimentation.providers.base.BaseExperimentationProvider"></a>

## BaseExperimentationProvider Objects

```python
class BaseExperimentationProvider(ABC)
```

A base class for experimentation providers.
All providers should inherit from this and implement the necessary methods.

<a id="wyvern.experimentation.providers.base.BaseExperimentationProvider.get_result"></a>

#### get_result

```python
@abstractmethod
def get_result(experiment_id: str, entity_id: str, **kwargs) -> str
```

Get the result (variant) for a given experiment and entity.

**Arguments**:

- experiment_id (str): The unique ID of the experiment.
- entity_id (str): The unique ID of the entity.
- kwargs (dict): Any additional arguments to pass to the provider for targeting.

**Returns**:

- str: The result (variant) assigned to the entity for the specified experiment.

<a id="wyvern.experimentation.providers.base.BaseExperimentationProvider.log_result"></a>

#### log_result

```python
@abstractmethod
def log_result(experiment_id: str,
               entity_id: str,
               variant: Optional[str] = None,
               has_error: bool = False,
               **kwargs) -> None
```

Log the result (variant) for a given experiment and entity.

**Arguments**:

- experiment_id (str): The unique ID of the experiment.
- entity_id (str): The unique ID of the entity.
- variant (str): The result (variant) assigned to the entity for the specified experiment.
- kwargs (dict): Any additional arguments to pass to the provider for targeting.

**Returns**:

- None

<a id="wyvern.experimentation.client"></a>

# wyvern.experimentation.client

<a id="wyvern.experimentation.client.ExperimentationClient"></a>

## ExperimentationClient Objects

```python
class ExperimentationClient()
```

A client for interacting with experimentation providers.

<a id="wyvern.experimentation.client.ExperimentationClient.__init__"></a>

#### \_\_init\_\_

```python
def __init__(provider_name: str, api_key: Optional[str] = None)
```

Initializes the ExperimentationClient with a specified provider.

**Arguments**:

- provider_name (str): The name of the experimentation provider (e.g., "eppo").

<a id="wyvern.experimentation.client.ExperimentationClient.get_experiment_result"></a>

#### get_experiment_result

```python
def get_experiment_result(experiment_id: str, entity_id: str,
                          **kwargs) -> Optional[str]
```

Get the result (variant) for a given experiment and entity using the chosen provider.

**Arguments**:

- experiment_id (str): The unique ID of the experiment.
- entity_id (str): The unique ID of the entity.
- kwargs (dict): Any additional arguments to pass to the provider for targeting.

**Returns**:

- str: The result (variant) assigned to the entity for the specified experiment.

<a id="wyvern.experimentation"></a>

# wyvern.experimentation

<a id="wyvern.index"></a>

# wyvern.index

<a id="wyvern.request_context"></a>

# wyvern.request_context

<a id="wyvern.request_context.current"></a>

#### current

```python
def current() -> Optional[WyvernRequest]
```

Get the current request context

**Returns**:

The current request context, or None if there is none

<a id="wyvern.request_context.ensure_current_request"></a>

#### ensure_current_request

```python
def ensure_current_request() -> WyvernRequest
```

Get the current request context, or raise an error if there is none

**Returns**:

The current request context if there is one

**Raises**:

- `RuntimeError` - If there is no current request context

<a id="wyvern.request_context.set"></a>

#### set

```python
def set(request: WyvernRequest) -> None
```

Set the current request context

**Arguments**:

- `request` - The request context to set

**Returns**:

None

<a id="wyvern.request_context.reset"></a>

#### reset

```python
def reset() -> None
```

Reset the current request context

**Returns**:

None

<a id="wyvern.wyvern_typing"></a>

# wyvern.wyvern_typing

<a id="wyvern.wyvern_typing.WyvernFeature"></a>

#### WyvernFeature

A WyvernFeature defines the type of a feature in Wyvern. It can be a float, a string, a list of floats, or None.

<a id="wyvern.cli.commands"></a>

# wyvern.cli.commands

<a id="wyvern.cli.commands.init"></a>

#### init

```python
@app.command()
def init(project: str = typer.Argument(...,
                                       help="Name of the project")) -> None
```

Initializes Wyvern application template code

**Arguments**:

- `project` _str_ - Name of the project

<a id="wyvern.cli.commands.run"></a>

#### run

```python
@app.command()
def run(
    path: str = "pipelines.main:app",
    host: Annotated[
        str,
        typer.Option(help="Host to run the application on"),
    ] = "0.0.0.0",
    port: Annotated[
        int,
        typer.Option(
            help="Port to run the application on. Default port is 5001"),
    ] = 5001
) -> None
```

Starts Wyvern application server

Example usage:
wyvern run --path pipelines.main:app --host 0.0.0.0 --port 5001

**Arguments**:

- `path` _str_ - path to the wyvern app. Default path is pipelines.main:app
- `host` _str_ - Host to run the application on. Default host is 0.0.0.0
- `port` _int_ - Port to run the application on. Default port is 5001

<a id="wyvern.cli.commands.redis"></a>

#### redis

```python
@app.command()
def redis() -> None
```

Starts Redis server. This command will also install redis locally if it's not installed.

<a id="wyvern.api"></a>

# wyvern.api

<a id="wyvern.api.ensure_async_client"></a>

#### ensure_async_client

```python
def ensure_async_client(func: Callable) -> Callable
```

Ensure that the async client is open before calling the function and close it after calling the function

**Arguments**:

- `func` - The function to be wrapped

**Returns**:

The wrapped function

<a id="wyvern.api.WyvernAPI"></a>

## WyvernAPI Objects

```python
class WyvernAPI()
```

Wyvern API client

<a id="wyvern.api.WyvernAPI.get_historical_features"></a>

#### get_historical_features

```python
@ensure_async_client
def get_historical_features(
        features: List[str], entities: Union[Dict[Hashable, List[Any]],
                                             pd.DataFrame]) -> pd.DataFrame
```

Aggregate all the historical features, including the offline features in your data warehouse
and the historical real-time features being consumed by wyvern pipeline.

**Arguments**:

- `features` - A list of feature names.
- `entities` - A dictionary or pandas DataFrame of entity names and their values.
  some requirements of entities:
  - entities must have request and timestamp keys
  - request is a list of the request_id of request getting into Wyvern's pipeline
  - timestamp is a list of timestamp of the request
  - the rest of the columns are the entity for the features and the user interaction data

**Returns**:

A pandas DataFrame with all the feature data you're requesting from the entities.

<a id="wyvern.components.candidates"></a>

# wyvern.components.candidates

<a id="wyvern.components.candidates.candidate_logger"></a>

# wyvern.components.candidates.candidate_logger

<a id="wyvern.components.candidates.candidate_logger.CandidateEventData"></a>

## CandidateEventData Objects

```python
class CandidateEventData(EntityEventData)
```

Event data for a candidate event

**Attributes**:

- `candidate_score` - The score of the candidate
- `candidate_order` - The order of the candidate in the list of candidates

<a id="wyvern.components.pagination.pagination_component"></a>

# wyvern.components.pagination.pagination_component

<a id="wyvern.components.pagination.pagination_component.PaginationRequest"></a>

## PaginationRequest Objects

```python
class PaginationRequest(GenericModel, Generic[T])
```

This is the input to the PaginationComponent.

**Attributes**:

- `pagination_fields` - The pagination fields that are used to compute the pagination.
- `entities` - The entities that need to be paginated.

<a id="wyvern.components.pagination.pagination_component.PaginationComponent"></a>

## PaginationComponent Objects

```python
class PaginationComponent(Component[PaginationRequest[T], List[T]])
```

This component is used to paginate the entities. It takes in the pagination fields and the entities and returns
the paginated entities.

<a id="wyvern.components.pagination.pagination_component.PaginationComponent.execute"></a>

#### execute

```python
async def execute(input: PaginationRequest[T], **kwargs) -> List[T]
```

This method paginates the entities based on the pagination fields.

Validations:

1. The ranking page should be greater than or equal to 0.
2. The candidate page should be greater than or equal to 0.
3. The candidate page size should be less than or equal to 1000.
4. The number of entities should be less than or equal to 1000.
5. The user page size should be less than or equal to 100.
6. The user page size should be less than or equal to the candidate page size.
7. The end index should be less than the number of entities.
8. The end index should be greater than the start index.

**Returns**:

The paginated entities.

<a id="wyvern.components.pagination"></a>

# wyvern.components.pagination

<a id="wyvern.components.pagination.pagination_fields"></a>

# wyvern.components.pagination.pagination_fields

<a id="wyvern.components.pagination.pagination_fields.PaginationFields"></a>

## PaginationFields Objects

```python
class PaginationFields(BaseModel)
```

Pagination fields for requests. This is a mixin class that can be used in any request that requires pagination.

**Attributes**:

- `user_page_size` - Zero-indexed user facing page number
- `user_page` - Number of items per user facing page
- `candidate_page_size` - This is the size of the candidate page.
- `candidate_page` - This is the zero-indexed page number for the candidate set

<a id="wyvern.components.features.realtime_features_component"></a>

# wyvern.components.features.realtime_features_component

<a id="wyvern.components.features.realtime_features_component.PRIMARY_ENTITY"></a>

#### PRIMARY_ENTITY

The primary entity is the entity that is the main entity for the feature. For example, if we are computing
the feature for a user, the primary entity would be the user.

<a id="wyvern.components.features.realtime_features_component.SECONDARY_ENTITY"></a>

#### SECONDARY_ENTITY

The secondary entity is the entity that is the secondary entity for the feature. For example, if we are computing
the feature for a user and a product, the secondary entity would be the product. If we are computing the feature
for a user, the secondary entity would be None.

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureRequest"></a>

## RealtimeFeatureRequest Objects

```python
class RealtimeFeatureRequest(GenericModel, Generic[REQUEST_ENTITY])
```

This is the request that is passed into the realtime feature component.

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureEntity"></a>

## RealtimeFeatureEntity Objects

```python
class RealtimeFeatureEntity(GenericModel, Generic[PRIMARY_ENTITY,
                                                  SECONDARY_ENTITY])
```

This is the entity that is passed into the realtime feature component. It contains the primary entity and
the secondary entity. If the feature is only for the primary entity, the secondary entity will be None.

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent"></a>

## RealtimeFeatureComponent Objects

```python
class RealtimeFeatureComponent(Component[
        Tuple[
            RealtimeFeatureRequest[REQUEST_ENTITY],
            RealtimeFeatureEntity[PRIMARY_ENTITY, SECONDARY_ENTITY],
        ],
        Optional[FeatureData],
], Generic[PRIMARY_ENTITY, SECONDARY_ENTITY, REQUEST_ENTITY])
```

This is the base class for all realtime feature components. It contains the logic for computing the realtime
feature. The realtime feature component can be used to compute features for a single entity, two entities, or
a request. The realtime feature component can also be used to compute composite features for two entities.

The realtime feature component is a generic class that takes in the primary entity, secondary entity, and request
entity as type parameters. The primary entity is the entity that is the main entity for the feature. For example,
if we are computing the feature for a user, the primary entity would be the user. The secondary entity is the
entity that is the secondary entity for the feature. For example, if we are computing the feature for a user and
a product, the secondary entity would be the product. If we are computing the feature for a user, the secondary
entity would be None. The request entity is the request that is passed into the realtime feature component. We can
use the request entity to compute features for a request. For example, if we are computing the realtime features for
a ranking request, the request entity would be the ranking request. We can combine the primary entity, secondary
entity, and request entity to compute composite features.

**Attributes**:

- `NAME` - The name of the realtime feature component. This is used to identify the realtime feature component.
- `real_time_features` - A list of all the realtime feature components.
- `component_registry` - A dictionary that maps the name of the realtime feature component to the realtime feature

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*upstreams: Component,
             output_feature_names: Optional[Set[str]] = None,
             required_feature_names: Optional[Set[str]] = None,
             name: Optional[str] = None)
```

**Arguments**:

- `name`: Name of the component
- `output_feature_names`: features outputted by this real-time feature

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent.get_type_args_simple"></a>

#### get_type_args_simple

```python
@classmethod
def get_type_args_simple(cls, index: int) -> Type
```

Get the type argument at the given index for the class. This is used to get the primary entity type, secondary
entity type, and request entity type.

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent.get_entity_names"></a>

#### get_entity_names

```python
@classmethod
def get_entity_names(cls, full_feature_name: str) -> Optional[List[str]]
```

Get the entity identifier type, which will be used as sql column name

full_feature_name is of the form `<component_name>:<feature_name>`

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent.get_entity_type_column"></a>

#### get_entity_type_column

```python
@classmethod
def get_entity_type_column(cls, full_feature_name: str) -> Optional[str]
```

Get the entity identifier type, which will be used as sql column name

full_feature_name is of the form `<component_name>:<feature_name>`

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent.can_execute_on"></a>

#### can_execute_on

```python
def can_execute_on(request: REQUEST_ENTITY,
                   primary_entity: Optional[PRIMARY_ENTITY],
                   secondary_entity: Optional[SECONDARY_ENTITY]) -> bool
```

Checks if the input matches the entity type, so we can execute on it

<a id="wyvern.components.features.realtime_features_component.RealtimeFeatureComponent.set_full_feature_name"></a>

#### set_full_feature_name

```python
def set_full_feature_name(
        feature_data: Optional[FeatureData]) -> Optional[FeatureData]
```

Sets the full feature name for the feature data

<a id="wyvern.components.features.feature_store"></a>

# wyvern.components.features.feature_store

<a id="wyvern.components.features.feature_store.FeatureStoreRetrievalRequest"></a>

## FeatureStoreRetrievalRequest Objects

```python
class FeatureStoreRetrievalRequest(BaseModel)
```

Request to retrieve features from the feature store.

**Attributes**:

- `identifiers` - List of identifiers for which features are to be retrieved.
- `feature_names` - List of feature names to be retrieved. Feature names are of the form
  `<feature_view_name>:<feature_name>`.

<a id="wyvern.components.features.feature_store.FeatureStoreRetrievalComponent"></a>

## FeatureStoreRetrievalComponent Objects

```python
class FeatureStoreRetrievalComponent(Component[FeatureStoreRetrievalRequest,
                                               FeatureMap])
```

Component to retrieve features from the feature store. This component is responsible for fetching features from
the feature store and returning them in the form of a FeatureMap. The FeatureMap is a mapping from identifiers to
FeatureData. The FeatureData contains the identifier and a mapping from feature names to feature values. The
feature names are of the form `<feature_view_name>:<feature_name>`. The feature values are of type WyvernFeature
which is a union of all the possible feature types. The feature types are defined in `wyvern/wyvern_typing.py`.
The FeatureStoreRetrievalComponent is a singleton and can be accessed via `feature_store_retrieval_component`.

The FeatureStoreRetrievalComponent is configured via the following environment variables:

- WYVERN_API_KEY: if you're using Wyvern's feature store, this is the API key for Wyvern
- WYVERN_FEATURE_STORE_URL: url to the feature store
- WYVERN_ONLINE_FEATURES_PATH: url path to the feature store's online features endpoint
- FEATURE_STORE_ENABLED: whether the feature store is enabled or not

<a id="wyvern.components.features.feature_store.FeatureStoreRetrievalComponent.fetch_features_from_feature_store"></a>

#### fetch_features_from_feature_store

```python
async def fetch_features_from_feature_store(
        identifiers: List[Identifier], feature_names: List[str]) -> FeatureMap
```

Fetches features from the feature store for the given identifiers and feature names.

**Arguments**:

- `identifiers` - List of identifiers for which features are to be retrieved.
- `feature_names` - List of feature names to be retrieved.

**Returns**:

FeatureMap containing the features for the given identifiers and feature names.

<a id="wyvern.components.features.feature_store.FeatureStoreRetrievalComponent.execute"></a>

#### execute

```python
@tracer.wrap(name="FeatureStoreRetrievalComponent.execute")
async def execute(input: FeatureStoreRetrievalRequest,
                  handle_exceptions: bool = False,
                  **kwargs) -> FeatureMap
```

Fetches features from the feature store for the given identifiers and feature names. This method is a wrapper
around `fetch_features_from_feature_store` which handles exceptions and returns an empty FeatureMap in case of
an exception.

<a id="wyvern.components.features.feature_retrieval_pipeline"></a>

# wyvern.components.features.feature_retrieval_pipeline

<a id="wyvern.components.features.feature_retrieval_pipeline.FeatureRetrievalPipelineRequest"></a>

## FeatureRetrievalPipelineRequest Objects

```python
class FeatureRetrievalPipelineRequest(GenericModel, Generic[REQUEST_ENTITY])
```

This is the input to the FeatureRetrievalPipeline component that is used to retrieve features.

**Attributes**:

- `request` - The request that is used to retrieve features. This is used to retrieve the entities and
  identifiers that are needed to compute the features.
- `requested_feature_names` - The feature names that are
  requested. This is used to filter out the real-time features that are calculated instead of
  retrieved from the feature store. ie: `product_fv:FEATURE_PRODUCT_AMOUNT_PAID_LAST_15_DAYS`
- `feature_overrides` - This is used to override the default real-time features.

<a id="wyvern.components.features.feature_retrieval_pipeline.FeatureRetrievalPipeline"></a>

## FeatureRetrievalPipeline Objects

```python
class FeatureRetrievalPipeline(
        Component[FeatureRetrievalPipelineRequest[REQUEST_ENTITY],
                  FeatureMap], Generic[REQUEST_ENTITY])
```

This component is used to retrieve features for a given request. It is composed of the following components: 1. FeatureStoreRetrievalComponent: This component is used to retrieve features from the feature store. 2. RealtimeFeatureComponent: This component is used to compute real-time features. 3. FeatureEventLoggingComponent: This component is used to log feature events.

<a id="wyvern.components.features.feature_retrieval_pipeline.FeatureRetrievalPipeline.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*upstreams: Component,
             name: str,
             handle_exceptions: bool = False)
```

**Arguments**:

- `*upstreams` - The upstream components to this component.
- `name` - The name of this component.
- `handle_exceptions` - Whether to handle feature store exceptions. Defaults to False.
  If True, missing feature values will be None instead of raising exceptions.
  If False, exceptions will be raised.

<a id="wyvern.components.features.feature_retrieval_pipeline.FeatureRetrievalPipeline.execute"></a>

#### execute

```python
@tracer.wrap(name="FeatureRetrievalPipeline.execute")
async def execute(input: FeatureRetrievalPipelineRequest[REQUEST_ENTITY],
                  **kwargs) -> FeatureMap
```

This method is used to retrieve features for a given request.

It is composed of the following steps: 0. Figure out which features are real-time features and which features are feature store features. 1. Retrieve features from the feature store. 2. Compute real-time features. 3. Combine the feature store features and real-time features into one FeatureMap. 4. Log the feature values to the feature event logging component.

<a id="wyvern.components.features"></a>

# wyvern.components.features

<a id="wyvern.components.features.feature_logger"></a>

# wyvern.components.features.feature_logger

<a id="wyvern.components.features.feature_logger.FeatureLogEventData"></a>

## FeatureLogEventData Objects

```python
class FeatureLogEventData(BaseModel)
```

Data for a feature event.

**Attributes**:

- `feature_identifier` - The identifier of the feature.
- `feature_identifier_type` - The type of the feature identifier.
- `feature_name` - The name of the feature.
- `feature_value` - The value of the feature.

<a id="wyvern.components.features.feature_logger.FeatureEvent"></a>

## FeatureEvent Objects

```python
class FeatureEvent(LoggedEvent[FeatureLogEventData])
```

A feature event.

**Attributes**:

- `event_type` - The type of the event. Defaults to EventType.FEATURE.

<a id="wyvern.components.features.feature_logger.FeatureEventLoggingRequest"></a>

## FeatureEventLoggingRequest Objects

```python
class FeatureEventLoggingRequest(GenericModel, Generic[REQUEST_ENTITY])
```

A request to log feature events.

**Attributes**:

- `request` - The request to log feature events for.
- `feature_map` - The feature map to log.

<a id="wyvern.components.features.feature_logger.FeatureEventLoggingComponent"></a>

## FeatureEventLoggingComponent Objects

```python
class FeatureEventLoggingComponent(
        Component[FeatureEventLoggingRequest[REQUEST_ENTITY],
                  None], Generic[REQUEST_ENTITY])
```

A component that logs feature events.

<a id="wyvern.components.features.feature_logger.FeatureEventLoggingComponent.execute"></a>

#### execute

```python
async def execute(input: FeatureEventLoggingRequest[REQUEST_ENTITY],
                  **kwargs) -> None
```

Logs feature events.

<a id="wyvern.components"></a>

# wyvern.components

<a id="wyvern.components.models.model_component"></a>

# wyvern.components.models.model_component

<a id="wyvern.components.models.model_component.MODEL_OUTPUT_DATA_TYPE"></a>

#### MODEL_OUTPUT_DATA_TYPE

MODEL_OUTPUT_DATA_TYPE is the type of the output of the model. It can be a float, a string, or a list of floats
(e.g. a list of probabilities, embeddings, etc.)

<a id="wyvern.components.models.model_component.ModelEventData"></a>

## ModelEventData Objects

```python
class ModelEventData(BaseModel)
```

This class defines the data that will be logged for each model event.

**Arguments**:

- `model_name` - The name of the model
- `model_output` - The output of the model
- `entity_identifier` - The identifier of the entity that was used to generate the model output. This is optional.
- `entity_identifier_type` - The type of the identifier of the entity that was used to generate the model output.
  This is optional.

<a id="wyvern.components.models.model_component.ModelEvent"></a>

## ModelEvent Objects

```python
class ModelEvent(LoggedEvent[ModelEventData])
```

Model event. This is the event that is logged when a model is evaluated.

**Arguments**:

- `event_type` - The type of the event. This is always EventType.MODEL.

<a id="wyvern.components.models.model_component.ModelOutput"></a>

## ModelOutput Objects

```python
class ModelOutput(GenericModel, Generic[MODEL_OUTPUT_DATA_TYPE])
```

This class defines the output of a model.

**Arguments**:

- `data` - A dictionary mapping entity identifiers to model outputs. The model outputs can also be None.
- `model_name` - The name of the model. This is optional.

<a id="wyvern.components.models.model_component.ModelOutput.get_entity_output"></a>

#### get_entity_output

```python
def get_entity_output(
        identifier: Identifier) -> Optional[MODEL_OUTPUT_DATA_TYPE]
```

Get the model output for a given entity identifier.

**Arguments**:

- `identifier` - The identifier of the entity.

**Returns**:

The model output for the given entity identifier. This can also be None if the model output is None.

<a id="wyvern.components.models.model_component.ModelInput"></a>

## ModelInput Objects

```python
class ModelInput(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY,
                                       REQUEST_ENTITY])
```

This class defines the input to a model.

**Arguments**:

- `request` - The request that will be used to generate the model input.
- `entities` - A list of entities that will be used to generate the model input.

<a id="wyvern.components.models.model_component.ModelInput.first_entity"></a>

#### first_entity

```python
@property
def first_entity() -> GENERALIZED_WYVERN_ENTITY
```

Get the first entity in the list of entities. This is useful when you know that there is only one entity.

**Returns**:

The first entity in the list of entities.

<a id="wyvern.components.models.model_component.ModelInput.first_identifier"></a>

#### first_identifier

```python
@property
def first_identifier() -> Identifier
```

Get the identifier of the first entity in the list of entities. This is useful when you know that there is only
one entity.

**Returns**:

The identifier of the first entity in the list of entities.

<a id="wyvern.components.models.model_component.ModelComponent"></a>

## ModelComponent Objects

```python
class ModelComponent(Component[
        MODEL_INPUT,
        MODEL_OUTPUT,
])
```

This class defines a model component. A model component is a component that takes in a request and a list of
entities and outputs a model output. The model output is a dictionary mapping entity identifiers to model outputs.
The model outputs can also be None if the model output is None for a given entity.

<a id="wyvern.components.models.model_component.ModelComponent.get_type_args_simple"></a>

#### get_type_args_simple

```python
@classmethod
def get_type_args_simple(cls, index: int) -> Type
```

Get the type argument at the given index. This is used to get the model input and model output types.

<a id="wyvern.components.models.model_component.ModelComponent.manifest_feature_names"></a>

#### manifest_feature_names

```python
@cached_property
def manifest_feature_names() -> Set[str]
```

This function defines which features are necessary for model evaluation

Our system will automatically fetch the required features from the feature store
to make this model evaluation possible

<a id="wyvern.components.models.model_component.ModelComponent.execute"></a>

#### execute

```python
async def execute(input: MODEL_INPUT, **kwargs) -> MODEL_OUTPUT
```

The model_name and model_score will be automatically logged

<a id="wyvern.components.models.model_component.ModelComponent.batch_inference"></a>

#### batch_inference

```python
async def batch_inference(
    request: BaseWyvernRequest, entities: List[Union[WyvernEntity,
                                                     BaseWyvernRequest]]
) -> Sequence[Optional[Union[float, str, List[float]]]]
```

Define your model inference in a batched manner so that it's easier to boost inference speed

<a id="wyvern.components.models.model_component.ModelComponent.inference"></a>

#### inference

```python
async def inference(input: MODEL_INPUT, **kwargs) -> MODEL_OUTPUT
```

The inference function is the main entrance to model evaluation.

By default, the base ModelComponent slices entities into smaller batches and call batch_inference on each batch.

The default batch size is 30. You should be able to configure the MODEL_BATCH_SIZE env variable
to change the batch size.

In order to set up model inference, you only need to define a class that inherits ModelComponent and
implement batch_inference.

You can also override this function if you want to customize the inference logic.

<a id="wyvern.components.models"></a>

# wyvern.components.models

<a id="wyvern.components.models.modelbit_component"></a>

# wyvern.components.models.modelbit_component

<a id="wyvern.components.models.modelbit_component.ModelbitComponent"></a>

## ModelbitComponent Objects

```python
class ModelbitComponent(ModelComponent[MODEL_INPUT, MODEL_OUTPUT])
```

ModelbitComponent is a base class for all modelbit model components. It provides a common interface to implement
all modelbit models.

ModelbitComponent is a subclass of ModelComponent.

**Attributes**:

- `AUTH_TOKEN` - A class variable that stores the auth token for Modelbit.
- `URL` - A class variable that stores the url for Modelbit.

<a id="wyvern.components.models.modelbit_component.ModelbitComponent.__init__"></a>

#### \_\_init\_\_

```python
def __init__(*upstreams,
             name: Optional[str] = None,
             auth_token: Optional[str] = None,
             url: Optional[str] = None) -> None
```

**Arguments**:

- `*upstreams` - A list of upstream components.
- `name` - A string that represents the name of the model.
- `auth_token` - A string that represents the auth token for Modelbit.
- `url` - A string that represents the url for Modelbit.

**Raises**:

- `WyvernModelbitTokenMissingError` - If the auth token is not provided.

<a id="wyvern.components.models.modelbit_component.ModelbitComponent.modelbit_features"></a>

#### modelbit_features

```python
@cached_property
def modelbit_features() -> List[str]
```

This is a cached property that returns a list of modelbit features. This method should be implemented by the
subclass.

<a id="wyvern.components.models.modelbit_component.ModelbitComponent.manifest_feature_names"></a>

#### manifest_feature_names

```python
@cached_property
def manifest_feature_names() -> Set[str]
```

This is a cached property that returns a set of manifest feature names. This method wraps around the
modelbit_features property.

<a id="wyvern.components.models.modelbit_component.ModelbitComponent.build_requests"></a>

#### build_requests

```python
async def build_requests(
        input: MODEL_INPUT) -> Tuple[List[Identifier], List[Any]]
```

Please refer to modlebit batch inference API:
https://doc.modelbit.com/deployments/rest-api/

<a id="wyvern.components.models.modelbit_component.ModelbitComponent.inference"></a>

#### inference

```python
async def inference(input: MODEL_INPUT, **kwargs) -> MODEL_OUTPUT
```

This method sends a request to Modelbit and returns the output.

<a id="wyvern.components.api_route_component"></a>

# wyvern.components.api_route_component

<a id="wyvern.components.api_route_component.APIRouteComponent"></a>

## APIRouteComponent Objects

```python
class APIRouteComponent(Component[REQUEST_SCHEMA, RESPONSE_SCHEMA])
```

APIRouteComponent is the base class for all the API routes in Wyvern. It is a Component that
takes in a request schema and a response schema, and it is responsible for hydrating the request
data with Wyvern Index data, and then pass the hydrated data to the next component in the pipeline.

The APIRouteComponent is also responsible for the API routing, which means it is responsible for
the API versioning and the API path.

**Attributes**:

- `API_VERSION` - the version of the API. This is used in the API routing. The default value is "v1".
- `PATH` - the path of the API. This is used in the API routing.
- `REQUEST_SCHEMA_CLASS` - the class of the request schema. This is used to validate the request data.
- `RESPONSE_SCHEMA_CLASS` - the class of the response schema. This is used to validate the response data.
- `API_NAME` - the name of the API. This is used in the API routing. If not provided, the name of the
  APIRouteComponent will be used.

<a id="wyvern.components.api_route_component.APIRouteComponent.warm_up"></a>

#### warm_up

```python
async def warm_up(input: REQUEST_SCHEMA) -> None
```

This is the warm-up function that is called before the API route is called.

<a id="wyvern.components.api_route_component.APIRouteComponent.hydrate"></a>

#### hydrate

```python
@tracer.wrap(name="APIRouteComponent.hydrate")
async def hydrate(input: REQUEST_SCHEMA) -> None
```

Wyvern APIRouteComponent recursively hydrate the request input data with Wyvern Index data

TODO: this function could be moved to a global place

<a id="wyvern.components.business_logic.boosting_business_logic"></a>

# wyvern.components.business_logic.boosting_business_logic

<a id="wyvern.components.business_logic.boosting_business_logic.BoostingBusinessLogicComponent"></a>

## BoostingBusinessLogicComponent Objects

```python
class BoostingBusinessLogicComponent(
        BusinessLogicComponent[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY])
```

A component that performs boosting on an entity with a set of candidates. The boosting can be multiplicative
or additive.

The request itself could contain more than just entities, for example it may contain a query and so on

<a id="wyvern.components.business_logic.boosting_business_logic.BoostingBusinessLogicComponent.boost"></a>

#### boost

```python
def boost(
        scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        entity_keys: Set[str],
        boost: float,
        entity_key_mapping: Callable[
            [GENERALIZED_WYVERN_ENTITY],
            str,
        ] = lambda candidate: candidate.identifier.identifier,
        multiplicative=False
) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]
```

Boosts the score of each candidate by a certain factor

**Arguments**:

- `scored_candidates` - The list of scored candidates
- `entity_keys` - The set of entity keys (unique identifiers) to boost
- `boost` - The boost factor
- `entity_key_mapping` - A lambda function that takes in a candidate entity and
  returns the field we should apply the boost to
- `multiplicative` - Whether to apply the boost with multiplication or addition - true indicates it is
  multiplication and false indicates it is addition

**Returns**:

The list of scored candidates with the boost applied

<a id="wyvern.components.business_logic.boosting_business_logic.CSVBoostingBusinessLogicComponent"></a>

## CSVBoostingBusinessLogicComponent Objects

```python
class CSVBoostingBusinessLogicComponent(
        BoostingBusinessLogicComponent[GENERALIZED_WYVERN_ENTITY,
                                       REQUEST_ENTITY],
        Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY])
```

This component reads a csv file and applies the boost based on specific column name, entity key, and score
combinations

Methods to define: Given a CSV row, generate the entity key and boost value

**Arguments**:

- `csv_file` - The path to the CSV file
- `multiplicative` - Whether to apply the boost with multiplication or addition - true indicates it is
  multiplication and false indicates it is addition

<a id="wyvern.components.business_logic.boosting_business_logic.CSVBoostingBusinessLogicComponent.initialize"></a>

#### initialize

```python
async def initialize() -> None
```

Reads the CSV file and populates the lookup table

<a id="wyvern.components.business_logic.boosting_business_logic.CSVBoostingBusinessLogicComponent.extract_keys_from_csv_row"></a>

#### extract_keys_from_csv_row

```python
@abstractmethod
async def extract_keys_from_csv_row(row: Series) -> str
```

Given a CSV row, generate the unique combinations that would apply a boost

Example, in a file that has the following:
product_id, query, boost

The method would return a unique concatenation (ie product_id:query)

<a id="wyvern.components.business_logic.boosting_business_logic.CSVBoostingBusinessLogicComponent.extract_boost_value_from_csv_row"></a>

#### extract_boost_value_from_csv_row

```python
@abstractmethod
async def extract_boost_value_from_csv_row(row: Series) -> float
```

Given a CSV row, generate the unique combinations that would apply a boost

Example, in a file that has the following:
product_id, query, boost

The method would return the boost value

<a id="wyvern.components.business_logic.boosting_business_logic.CSVBoostingBusinessLogicComponent.extract_key_from_request_entity"></a>

#### extract_key_from_request_entity

```python
@abstractmethod
async def extract_key_from_request_entity(candidate: GENERALIZED_WYVERN_ENTITY,
                                          request: REQUEST_ENTITY) -> str
```

Given a candidate and a request, generate a unique key that would apply a boost

<a id="wyvern.components.business_logic.boosting_business_logic.CSVBoostingBusinessLogicComponent.execute"></a>

#### execute

```python
async def execute(
        input: BusinessLogicRequest[
            GENERALIZED_WYVERN_ENTITY,
            REQUEST_ENTITY,
        ], **kwargs) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]
```

Boosts the score of each candidate by a certain factor

<a id="wyvern.components.business_logic"></a>

# wyvern.components.business_logic

<a id="wyvern.components.business_logic.business_logic"></a>

# wyvern.components.business_logic.business_logic

<a id="wyvern.components.business_logic.business_logic.BusinessLogicEventData"></a>

## BusinessLogicEventData Objects

```python
class BusinessLogicEventData(EntityEventData)
```

The data associated with a business logic event

**Arguments**:

- `business_logic_pipeline_order` - The order of the business logic pipeline that this event occurred in
- `business_logic_name` - The name of the business logic component that this event occurred in
- `old_score` - The old score of the entity
- `new_score` - The new score of the entity

<a id="wyvern.components.business_logic.business_logic.BusinessLogicEvent"></a>

## BusinessLogicEvent Objects

```python
class BusinessLogicEvent(LoggedEvent[BusinessLogicEventData])
```

An event that occurs in the business logic layer

<a id="wyvern.components.business_logic.business_logic.BusinessLogicRequest"></a>

## BusinessLogicRequest Objects

```python
class BusinessLogicRequest(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY,
                                                 REQUEST_ENTITY])
```

A request to the business logic layer to perform business logic on a set of candidates

**Arguments**:

- `request` - The request that the business logic layer is being asked to perform business logic on
- `scored_candidates` - The candidates that the business logic layer is being asked to perform business logic on

<a id="wyvern.components.business_logic.business_logic.BusinessLogicResponse"></a>

## BusinessLogicResponse Objects

```python
class BusinessLogicResponse(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY,
                                                  REQUEST_ENTITY])
```

The response from the business logic layer after performing business logic on a set of candidates

**Arguments**:

- `request` - The request that the business logic layer was asked to perform business logic on
- `adjusted_candidates` - The candidates that the business logic layer performed business logic on

<a id="wyvern.components.business_logic.business_logic.BusinessLogicComponent"></a>

## BusinessLogicComponent Objects

```python
class BusinessLogicComponent(Component[
        BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
], Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY])
```

A component that performs business logic on an entity with a set of candidates

The request itself could contain more than just entities, for example it may contain a query and so on

<a id="wyvern.components.business_logic.business_logic.BusinessLogicPipeline"></a>

## BusinessLogicPipeline Objects

```python
class BusinessLogicPipeline(Component[
        BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        BusinessLogicResponse[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
], Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY])
```

Steps through a series of business logic components and returns the final output

This operation is fully chained, meaning that the output of each business logic component is passed
as an input to the next business logic component

<a id="wyvern.components.business_logic.business_logic.BusinessLogicPipeline.execute"></a>

#### execute

```python
@tracer.wrap(name="BusinessLogicPipeline.execute")
async def execute(
    input: BusinessLogicRequest[GENERALIZED_WYVERN_ENTITY,
                                REQUEST_ENTITY], **kwargs
) -> BusinessLogicResponse[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY]
```

Executes the business logic pipeline on the inputted candidates

**Arguments**:

- `input` - The input to the business logic pipeline

**Returns**:

The output of the business logic pipeline

<a id="wyvern.components.business_logic.business_logic.BusinessLogicPipeline.extract_business_logic_events"></a>

#### extract_business_logic_events

```python
def extract_business_logic_events(
        output: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        pipeline_index: int, upstream_name: str, request_id: str,
        old_scores: List[float]) -> List[BusinessLogicEvent]
```

Extracts the business logic events from the output of a business logic component

**Arguments**:

- `output` - The output of a business logic component
- `pipeline_index` - The index of the business logic component in the business logic pipeline
- `upstream_name` - The name of the business logic component
- `request_id` - The request id of the request that the business logic component was called in
- `old_scores` - The old scores of the candidates that the business logic component was called on

**Returns**:

The business logic events that were extracted from the output of the business logic component

<a id="wyvern.components.business_logic.pinning_business_logic"></a>

# wyvern.components.business_logic.pinning_business_logic

<a id="wyvern.components.business_logic.pinning_business_logic.PinningBusinessLogicComponent"></a>

## PinningBusinessLogicComponent Objects

```python
class PinningBusinessLogicComponent(
        BusinessLogicComponent[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY],
        Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY])
```

A component that performs boosting on an entity with a set of candidates

The request itself could contain more than just entities, for example it may contain a query and so on

<a id="wyvern.components.business_logic.pinning_business_logic.PinningBusinessLogicComponent.pin"></a>

#### pin

```python
def pin(
    scored_candidates: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
    entity_pins: Dict[str, int],
    entity_key_mapping: Callable[
        [GENERALIZED_WYVERN_ENTITY],
        str,
    ] = lambda candidate: candidate.identifier.identifier,
    allow_down_ranking: bool = False
) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]
```

Pins the supplied entity to the specific position

**Arguments**:

- `scored_candidates` - The list of scored candidates
- `entity_pins` - The map of entity keys (unique identifiers) to pin, and their pinning position
- `entity_key_mapping` - A lambda function that takes in a candidate entity and
  returns the field we should apply the pin to
- `allow_down_ranking` - Whether to allow down-ranking of candidates that are not pinned

**Returns**:

The list of scored candidates with the pinned entities

<a id="wyvern.components.ranking_pipeline"></a>

# wyvern.components.ranking_pipeline

<a id="wyvern.components.ranking_pipeline.RankingRequest"></a>

## RankingRequest Objects

```python
class RankingRequest(BaseWyvernRequest, PaginationFields,
                     Generic[WYVERN_ENTITY])
```

This is the request for the ranking pipeline.

**Attributes**:

- `query` - the query entity
- `candidates` - the list of candidate entities

<a id="wyvern.components.ranking_pipeline.ResponseCandidate"></a>

## ResponseCandidate Objects

```python
class ResponseCandidate(BaseModel)
```

This is the response candidate.

**Attributes**:

- `candidate_id` - the identifier of the candidate
- `ranked_score` - the ranked score of the candidate

<a id="wyvern.components.ranking_pipeline.RankingResponse"></a>

## RankingResponse Objects

```python
class RankingResponse(BaseModel)
```

This is the response for the ranking pipeline.

**Attributes**:

- `ranked_candidates` - the list of ranked candidates
- `events` - the list of logged events

<a id="wyvern.components.ranking_pipeline.RankingPipeline"></a>

## RankingPipeline Objects

```python
class RankingPipeline(PipelineComponent[RankingRequest, RankingResponse],
                      Generic[WYVERN_ENTITY])
```

This is the ranking pipeline.

**Attributes**:

- `PATH` - the path of the API. This is used in the API routing. The default value is "/ranking".

<a id="wyvern.components.ranking_pipeline.RankingPipeline.get_model"></a>

#### get_model

```python
def get_model() -> ModelComponent
```

This is the ranking model.

The model input should be a subclass of ModelInput.
Its output should be scored candidates

<a id="wyvern.components.ranking_pipeline.RankingPipeline.get_business_logic"></a>

#### get_business_logic

```python
def get_business_logic() -> Optional[BusinessLogicPipeline]
```

This is the business logic pipeline. It is optional. If not provided, the ranking pipeline will not
apply any business logic.

The business logic pipeline should be a subclass of BusinessLogicPipeline. Some examples of business logic
for ranking pipeline are:

1. Deduplication
2. Filtering
3. (De)boosting

<a id="wyvern.components.ranking_pipeline.RankingPipeline.rank_candidates"></a>

#### rank_candidates

```python
async def rank_candidates(
    request: RankingRequest[WYVERN_ENTITY]
) -> List[ScoredCandidate[WYVERN_ENTITY]]
```

This function ranks the candidates.

1. It first calls the ranking model to get the model scores for the candidates.
2. It then calls the business logic pipeline to adjust the model scores.
3. It returns the adjusted candidates.

**Arguments**:

- `request` - the ranking request

**Returns**:

A list of ScoredCandidate

<a id="wyvern.components.index._index"></a>

# wyvern.components.index.\_index

<a id="wyvern.components.index._index.IndexUploadComponent"></a>

## IndexUploadComponent Objects

```python
class IndexUploadComponent(APIRouteComponent[IndexRequest, IndexResponse])
```

<a id="wyvern.components.index._index.IndexUploadComponent.execute"></a>

#### execute

```python
async def execute(input: IndexRequest, **kwargs) -> IndexResponse
```

bulk index entities with redis pipeline

<a id="wyvern.components.index"></a>

# wyvern.components.index

<a id="wyvern.components.impressions"></a>

# wyvern.components.impressions

<a id="wyvern.components.impressions.impression_logger"></a>

# wyvern.components.impressions.impression_logger

<a id="wyvern.components.impressions.impression_logger.ImpressionEventData"></a>

## ImpressionEventData Objects

```python
class ImpressionEventData(EntityEventData)
```

Impression event data. This is the data that is logged for each impression.

**Arguments**:

- `impression_score` - The score of the impression.
- `impression_order` - The order of the impression.

<a id="wyvern.components.impressions.impression_logger.ImpressionEvent"></a>

## ImpressionEvent Objects

```python
class ImpressionEvent(LoggedEvent[ImpressionEventData])
```

Impression event. This is the event that is logged for each impression.

**Arguments**:

- `event_type` - The type of the event. This is always EventType.IMPRESSION.

<a id="wyvern.components.impressions.impression_logger.ImpressionEventLoggingRequest"></a>

## ImpressionEventLoggingRequest Objects

```python
class ImpressionEventLoggingRequest(GenericModel,
                                    Generic[GENERALIZED_WYVERN_ENTITY,
                                            REQUEST_ENTITY])
```

Impression event logging request.

**Arguments**:

- `request` - The request that was made.
- `scored_impressions` - The scored impressions. This is a list of scored candidates.
  Each scored candidate has an entity and a score.

<a id="wyvern.components.impressions.impression_logger.ImpressionEventLoggingComponent"></a>

## ImpressionEventLoggingComponent Objects

```python
class ImpressionEventLoggingComponent(Component[
        ImpressionEventLoggingRequest[GENERALIZED_WYVERN_ENTITY,
                                      REQUEST_ENTITY],
        None,
], Generic[GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY])
```

Impression event logging component. This component logs impression events.

<a id="wyvern.components.impressions.impression_logger.ImpressionEventLoggingComponent.execute"></a>

#### execute

```python
@tracer.wrap(name="ImpressionEventLoggingComponent.execute")
async def execute(input: ImpressionEventLoggingRequest[
    GENERALIZED_WYVERN_ENTITY, REQUEST_ENTITY], **kwargs) -> None
```

Logs impression events.

**Arguments**:

- `input` - The input to the component. This contains the request and the scored impressions.

**Returns**:

None

<a id="wyvern.components.events.events"></a>

# wyvern.components.events.events

<a id="wyvern.components.events.events.EventType"></a>

## EventType Objects

```python
class EventType(str, Enum)
```

Enum for the different types of events that can be logged.

<a id="wyvern.components.events.events.LoggedEvent"></a>

## LoggedEvent Objects

```python
class LoggedEvent(GenericModel, Generic[EVENT_DATA])
```

Base class for all logged events.

**Attributes**:

- `request_id` - The request ID of the request that triggered the event.
- `api_source` - The API source of the request that triggered the event.
- `event_timestamp` - The timestamp of the event.
- `event_type` - The type of the event.
- `event_data` - The data associated with the event. This is a generic type that can be any subclass of BaseModel.

<a id="wyvern.components.events.events.EntityEventData"></a>

## EntityEventData Objects

```python
class EntityEventData(BaseModel)
```

Base class for all entity event data.

**Attributes**:

- `entity_identifier` - The identifier of the entity that the event is associated with.
- `entity_identifier_type` - The type of the entity identifier.

<a id="wyvern.components.events.events.CustomEvent"></a>

## CustomEvent Objects

```python
class CustomEvent(LoggedEvent[ENTITY_EVENT_DATA_TYPE])
```

Class for custom events. Custom event data must be a subclass of EntityEventData.

**Attributes**:

- `event_type` - The type of the event. This is always EventType.CUSTOM.

<a id="wyvern.components.events"></a>

# wyvern.components.events

<a id="wyvern.components.component"></a>

# wyvern.components.component

<a id="wyvern.components.component.ComponentStatus"></a>

## ComponentStatus Objects

```python
class ComponentStatus(str, Enum)
```

This enum defines the status of the component.

<a id="wyvern.components.component.Component"></a>

## Component Objects

```python
class Component(Generic[INPUT_TYPE, OUTPUT_TYPE])
```

Component is the base class for all the components in Wyvern. It is a generic class that takes in
the input type and the output type of the component.

It is responsible for: 1. Initializing the component 2. Initializing the upstream components

<a id="wyvern.components.component.Component.initialize"></a>

#### initialize

```python
async def initialize() -> None
```

This is the place where you can do some initialization work for your component

As an example, you can initialize a model here or load a file,
which is needed for your component to work

<a id="wyvern.components.component.Component.initialize_wrapper"></a>

#### initialize_wrapper

```python
async def initialize_wrapper() -> None
```

Extend this method if your component has some work that needs to be done on server startup

This is a great place to initialize libraries to access external libraries, warm up models, etc

This runs after all objects have been constructed

<a id="wyvern.components.component.Component.execute"></a>

#### execute

```python
async def execute(input: INPUT_TYPE, **kwargs) -> OUTPUT_TYPE
```

The actual meat of the component.
Custom component has to implement

If your component has to complex input data structure, make sure to override this method in order to
construct your input data with upstream components' output data

upstream_outputs contains data that was parsed by upstreams

<a id="wyvern.components.component.Component.manifest_feature_names"></a>

#### manifest_feature_names

```python
@cached_property
def manifest_feature_names() -> Set[str]
```

This function defines which features are required for this component to work

Our system will automatically fetch the required features from the feature store
to make this model evaluation possible

<a id="wyvern.components.component.Component.get_feature"></a>

#### get_feature

```python
def get_feature(identifier: Identifier, feature_name: str) -> WyvernFeature
```

This function gets the feature value for the given identifier
The features are cached once fetched/evaluated.

The feature that lives in the feature store should be
just using the feature name without the "feature_view:" prefix
For example, if your you have a feature view "fv" and a feature "wyvern_feature",
then you would have defined "fv:wyvern_feature" in manifest_feature_names.
However, when you fetch the feature value with this function,
you just have to pass in feature_name="wyvern_feature".

<a id="wyvern.components.component.Component.get_all_features"></a>

#### get_all_features

```python
def get_all_features(identifier: Identifier) -> Dict[str, WyvernFeature]
```

This function gets all features for the given identifier
The features are cached once fetched/evaluated.

<a id="wyvern.components.pipeline_component"></a>

# wyvern.components.pipeline_component

<a id="wyvern.components.pipeline_component.PipelineComponent"></a>

## PipelineComponent Objects

```python
class PipelineComponent(APIRouteComponent[REQUEST_ENTITY, RESPONSE_SCHEMA])
```

PipelineComponent is the base class for all the pipeline components in Wyvern. It is a Component that
takes in a request entity and a response schema, and it is responsible for hydrating the request
data with Wyvern Index data, and then pass the hydrated data to the next component in the pipeline.

<a id="wyvern.components.pipeline_component.PipelineComponent.realtime_features_overrides"></a>

#### realtime_features_overrides

```python
@cached_property
def realtime_features_overrides() -> Set[Type[RealtimeFeatureComponent]]
```

This function defines the set of RealtimeFeatureComponents that generates features
with non-deterministic feature names.
For example, feature names like matched*query_brand.
That feature is defined like matched_query*{input.query.matched_query}, so it can refer to 10 or 20 features

<a id="wyvern.components.pipeline_component.PipelineComponent.retrieve_features"></a>

#### retrieve_features

```python
async def retrieve_features(request: REQUEST_ENTITY) -> None
```

TODO shu: it doesn't support feature overrides. Write code to support that

<a id="wyvern.components.helpers.linear_algebra"></a>

# wyvern.components.helpers.linear_algebra

<a id="wyvern.components.helpers.linear_algebra.CosineSimilarityComponent"></a>

## CosineSimilarityComponent Objects

```python
class CosineSimilarityComponent(Component[List[Tuple[List[float],
                                                     List[float]]],
                                          List[float]])
```

A component that computes cosine similarity in parallel for all pairs of embeddings.

<a id="wyvern.components.helpers.linear_algebra.CosineSimilarityComponent.execute"></a>

#### execute

```python
async def execute(input: List[Tuple[List[float], List[float]]],
                  **kwargs) -> List[float]
```

Computes cosine similarity in parallel for all pairs of embeddings.

**Arguments**:

- `input` - List of tuples of embeddings to compute cosine similarity for.

**Returns**:

List of cosine similarities.

<a id="wyvern.components.helpers.linear_algebra.CosineSimilarityComponent.cosine_similarity"></a>

#### cosine_similarity

```python
async def cosine_similarity(embedding_1: List[float],
                            embedding_2: List[float]) -> float
```

Computes cosine similarity between two embeddings.

<a id="wyvern.components.helpers.sorting"></a>

# wyvern.components.helpers.sorting

<a id="wyvern.components.helpers.sorting.SortingComponent"></a>

## SortingComponent Objects

```python
class SortingComponent(Component[
        List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
])
```

Sorts a list of candidates based on a score.

<a id="wyvern.components.helpers.sorting.SortingComponent.execute"></a>

#### execute

```python
async def execute(
        input: List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]],
        descending=True,
        **kwargs) -> List[ScoredCandidate[GENERALIZED_WYVERN_ENTITY]]
```

Sorts a list of candidates based on a score.

**Arguments**:

- `input` - A list of candidates to be sorted. Each candidate must have a score.
- `descending` - Whether to sort in descending order. Defaults to True.

**Returns**:

A sorted list of candidates.

<a id="wyvern.components.helpers"></a>

# wyvern.components.helpers

<a id="wyvern.redis"></a>

# wyvern.redis

<a id="wyvern.redis.WyvernRedis"></a>

## WyvernRedis Objects

```python
class WyvernRedis()
```

WyvernRedis is a wrapper for redis client to help index your entities in redis with Wyvern's convention

<a id="wyvern.redis.WyvernRedis.__init__"></a>

#### \_\_init\_\_

```python
def __init__(scope: str = "",
             redis_host: Optional[str] = None,
             redis_port: Optional[int] = None) -> None
```

scope is used to prefix the redis key. You can use the environment variable PROJECT_NAME to set the scope.

<a id="wyvern.redis.WyvernRedis.get_entity"></a>

#### get_entity

```python
async def get_entity(entity_type: str,
                     entity_id: str) -> Optional[Dict[str, Any]]
```

get entity from redis

<a id="wyvern.redis.WyvernRedis.get_entities"></a>

#### get_entities

```python
async def get_entities(
        entity_type: str,
        entity_ids: Sequence[str]) -> List[Optional[Dict[str, Any]]]
```

get entity from redis

<a id="wyvern.redis.WyvernRedis.delete_entity"></a>

#### delete_entity

```python
async def delete_entity(entity_type: str, entity_id: str) -> None
```

delete entity from redis

<a id="wyvern.redis.WyvernRedis.delete_entities"></a>

#### delete_entities

```python
async def delete_entities(entity_type: str, entity_ids: Sequence[str]) -> None
```

delete entities from redis

<a id="wyvern.utils"></a>

# wyvern.utils

<a id="wyvern.wyvern_tracing"></a>

# wyvern.wyvern_tracing

<a id="wyvern.wyvern_tracing.setup_tracing"></a>

#### setup_tracing

```python
def setup_tracing()
```

Setup tracing for Wyvern service. Tracing is disabled in development mode and for healthcheck requests.

<a id="wyvern.wyvern_logging"></a>

# wyvern.wyvern_logging

<a id="wyvern.wyvern_logging.setup_logging"></a>

#### setup_logging

```python
def setup_logging()
```

Setup logging configuration by loading from log_config.yml file. Logs an error if the
file cannot be found or loaded and uses default logging configuration.

<a id="wyvern.exceptions"></a>

# wyvern.exceptions

<a id="wyvern.exceptions.WyvernError"></a>

## WyvernError Objects

```python
class WyvernError(Exception)
```

Base class for all Wyvern errors.

**Attributes**:

- `message` - The error message.
- `error_code` - The error code.

<a id="wyvern.exceptions.WyvernEntityValidationError"></a>

## WyvernEntityValidationError Objects

```python
class WyvernEntityValidationError(WyvernError)
```

Raised when entity data is invalid

<a id="wyvern.exceptions.PaginationError"></a>

## PaginationError Objects

```python
class PaginationError(WyvernError)
```

Raised when there is an error in pagination

<a id="wyvern.exceptions.WyvernRouteRegistrationError"></a>

## WyvernRouteRegistrationError Objects

```python
class WyvernRouteRegistrationError(WyvernError)
```

Raised when there is an error in registering a route

<a id="wyvern.exceptions.ComponentAlreadyDefinedInPipelineComponentError"></a>

## ComponentAlreadyDefinedInPipelineComponentError Objects

```python
class ComponentAlreadyDefinedInPipelineComponentError(WyvernError)
```

Raised when a component is already defined in a pipeline component

<a id="wyvern.exceptions.WyvernFeatureStoreError"></a>

## WyvernFeatureStoreError Objects

```python
class WyvernFeatureStoreError(WyvernError)
```

Raised when there is an error in feature store

<a id="wyvern.exceptions.WyvernFeatureNameError"></a>

## WyvernFeatureNameError Objects

```python
class WyvernFeatureNameError(WyvernError)
```

Raised when there is an error in feature name

<a id="wyvern.exceptions.WyvernModelInputError"></a>

## WyvernModelInputError Objects

```python
class WyvernModelInputError(WyvernError)
```

Raised when there is an error in model input

<a id="wyvern.exceptions.WyvernModelbitTokenMissingError"></a>

## WyvernModelbitTokenMissingError Objects

```python
class WyvernModelbitTokenMissingError(WyvernError)
```

Raised when modelbit token is missing

<a id="wyvern.exceptions.WyvernModelbitValidationError"></a>

## WyvernModelbitValidationError Objects

```python
class WyvernModelbitValidationError(WyvernError)
```

Raised when modelbit validation fails

<a id="wyvern.exceptions.WyvernAPIKeyMissingError"></a>

## WyvernAPIKeyMissingError Objects

```python
class WyvernAPIKeyMissingError(WyvernError)
```

Raised when api key is missing

<a id="wyvern.exceptions.ExperimentationProviderNotSupportedError"></a>

## ExperimentationProviderNotSupportedError Objects

```python
class ExperimentationProviderNotSupportedError(WyvernError)
```

Raised when experimentation provider is not supported

<a id="wyvern.exceptions.ExperimentationClientInitializationError"></a>

## ExperimentationClientInitializationError Objects

```python
class ExperimentationClientInitializationError(WyvernError)
```

Raised when experimentation client initialization fails

<a id="wyvern.aws.kinesis"></a>

# wyvern.aws.kinesis

<a id="wyvern.aws.kinesis.KinesisFirehoseStream"></a>

## KinesisFirehoseStream Objects

```python
class KinesisFirehoseStream(str, Enum)
```

Enum for Kinesis Firehose stream names

Usage:

```
>>> KinesisFirehoseStream.EVENT_STREAM.get_stream_name()
```

<a id="wyvern.aws.kinesis.KinesisFirehoseStream.get_stream_name"></a>

#### get_stream_name

```python
def get_stream_name(customer_specific: bool = True,
                    env_specific: bool = True) -> str
```

Returns the stream name for the given stream

**Arguments**:

- `customer_specific` - Whether the stream name should be customer specific
- `env_specific` - Whether the stream name should be environment specific

**Returns**:

The stream name

<a id="wyvern.aws.kinesis.WyvernKinesisFirehose"></a>

## WyvernKinesisFirehose Objects

```python
class WyvernKinesisFirehose()
```

Wrapper around boto3 Kinesis Firehose client

<a id="wyvern.aws.kinesis.WyvernKinesisFirehose.put_record_batch_callable"></a>

#### put_record_batch_callable

```python
def put_record_batch_callable(
        stream_name: KinesisFirehoseStream,
        record_generator: List[Callable[[], List[BaseModel]]])
```

Puts records to the given stream. This is a callable that can be used with FastAPI's BackgroundTasks. This
way events can be logged asynchronously after the response is sent to the client.

**Arguments**:

- `stream_name` _KinesisFirehoseStream_ - The stream to put records to
- `record_generator` _List[Callable[[], List[BaseModel]]]_ - A list of functions that return a list of records

**Returns**:

None

<a id="wyvern.aws.kinesis.WyvernKinesisFirehose.put_record_batch"></a>

#### put_record_batch

```python
def put_record_batch(stream_name: KinesisFirehoseStream,
                     records: List[BaseModel])
```

Puts records to the given stream

**Arguments**:

- `stream_name` _KinesisFirehoseStream_ - The stream to put records to
- `records` _List[BaseModel]_ - A list of records

**Returns**:

None

<a id="wyvern.aws"></a>

# wyvern.aws

<a id="wyvern.event_logging"></a>

# wyvern.event_logging

<a id="wyvern.event_logging.event_logger"></a>

# wyvern.event_logging.event_logger

<a id="wyvern.event_logging.event_logger.log_events"></a>

#### log_events

```python
def log_events(event_generator: Callable[[], List[LoggedEvent]])
```

Logs events to the current request context.

**Arguments**:

- `event_generator` - A function that returns a list of events to be logged.

<a id="wyvern.event_logging.event_logger.get_logged_events"></a>

#### get_logged_events

```python
def get_logged_events() -> List[LoggedEvent[Any]]
```

**Returns**:

A list of all the events logged in the current request context.

<a id="wyvern.event_logging.event_logger.get_logged_events_generator"></a>

#### get_logged_events_generator

```python
def get_logged_events_generator(
) -> List[Callable[[], List[LoggedEvent[Any]]]]
```

**Returns**:

A list of all the event generators logged in the current request context.

<a id="wyvern.event_logging.event_logger.log_custom_events"></a>

#### log_custom_events

```python
def log_custom_events(events: List[ENTITY_EVENT_DATA_TYPE]) -> None
```

Logs custom events to the current request context.

**Arguments**:

- `events` - A list of custom events to be logged.

<a id="wyvern.web_frameworks.fastapi"></a>

# wyvern.web_frameworks.fastapi

<a id="wyvern.web_frameworks.fastapi.lifespan"></a>

#### lifespan

```python
@asynccontextmanager
async def lifespan(app: FastAPI)
```

A context manager that starts and stops with the app. This is used to start and stop the aiohttp client.

<a id="wyvern.web_frameworks.fastapi.WyvernFastapi"></a>

## WyvernFastapi Objects

```python
class WyvernFastapi()
```

A wrapper around FastAPI that provides a few additional features:

- A healthcheck endpoint
- A request middleware that logs the request and response payloads
- A request middleware that sets the WyvernRequest in the request context
- Auto registration of routes from APIRouteComponent subclasses

endpoint input:
the built WyvernPipeline
the request input schema
the request output schema

<a id="wyvern.web_frameworks.fastapi.WyvernFastapi.register_route"></a>

#### register_route

```python
async def register_route(route_component: Type[APIRouteComponent]) -> None
```

Register a route component. This will register the route with FastAPI and also initialize the route component.

**Arguments**:

- `route_component` - The route component to register.

**Raises**:

- `WyvernRouteRegistrationError` - If the route component is not a subclass of APIRouteComponent.

<a id="wyvern.web_frameworks"></a>

# wyvern.web_frameworks

<a id="wyvern.wyvern_request"></a>

# wyvern.wyvern_request

<a id="wyvern.wyvern_request.WyvernRequest"></a>

## WyvernRequest Objects

```python
@dataclass
class WyvernRequest()
```

WyvernRequest is a dataclass that represents a request to the Wyvern service. It is used to pass
information between the various components of the Wyvern service.

**Attributes**:

- `method` - The HTTP method of the request
- `url` - The full URL of the request
- `url_path` - The path of the URL of the request
- `json` - The JSON body of the request, represented by pydantic model
- `headers` - The headers of the request
- `entity_store` - A dictionary that can be used to store entities that are created during the request
- `events` - A list of functions that return a list of LoggedEvents. These functions are called at the end of
  the request to log events to the event store
- `feature_map` - A FeatureMap that can be used to store features that are created during the request
- `request_id` - The request ID of the request

<a id="wyvern.wyvern_request.WyvernRequest.parse_fastapi_request"></a>

#### parse_fastapi_request

```python
@classmethod
def parse_fastapi_request(cls,
                          json: BaseModel,
                          req: fastapi.Request,
                          request_id: Optional[str] = None) -> WyvernRequest
```

Parses a FastAPI request into a WyvernRequest

**Arguments**:

- `json` - The JSON body of the request, represented by pydantic model
- `req` - The FastAPI request
- `request_id` - The request ID of the request

**Returns**:

A WyvernRequest

<a id="wyvern.tracking"></a>

# wyvern.tracking

<a id="wyvern.feature_store.constants"></a>

# wyvern.feature_store.constants

<a id="wyvern.feature_store"></a>

# wyvern.feature_store

<a id="wyvern.feature_store.schemas"></a>

# wyvern.feature_store.schemas

<a id="wyvern.feature_store.schemas.GetOnlineFeaturesRequest"></a>

## GetOnlineFeaturesRequest Objects

```python
class GetOnlineFeaturesRequest(BaseModel)
```

Request object for getting online features.

**Attributes**:

- `entities` - A dictionary of entity name to entity value.
- `features` - A list of feature names.
- `full_feature_names` - A boolean indicating whether to return full feature names. If True, the feature names will
  be returned in the format `<feature_view_name>__<feature_name>`. If False, only the feature names will be
  returned.

<a id="wyvern.feature_store.schemas.GetHistoricalFeaturesRequest"></a>

## GetHistoricalFeaturesRequest Objects

```python
class GetHistoricalFeaturesRequest(BaseModel)
```

Request object for getting historical features.

**Attributes**:

- `entities` - A dictionary of entity name to entity value.
- `timestamps` - A list of timestamps. Used to retrieve historical features at specific timestamps. If not provided,
  the latest feature values will be returned.
- `features` - A list of feature names.

<a id="wyvern.feature_store.schemas.GetFeastHistoricalFeaturesRequest"></a>

## GetFeastHistoricalFeaturesRequest Objects

```python
class GetFeastHistoricalFeaturesRequest(BaseModel)
```

Request object for getting historical features from Feast.

**Attributes**:

- `full_feature_names` - A boolean indicating whether to return full feature names. If True, the feature names will
  be returned in the format `<feature_view_name>__<feature_name>`. If False, only the feature names will be
  returned.
- `entities` - A dictionary of entity name to entity value.
- `features` - A list of feature names.

<a id="wyvern.feature_store.schemas.GetHistoricalFeaturesResponse"></a>

## GetHistoricalFeaturesResponse Objects

```python
class GetHistoricalFeaturesResponse(BaseModel)
```

Response object for getting historical features.

**Attributes**:

- `results` - A list of dictionaries containing feature values.

<a id="wyvern.feature_store.schemas.MaterializeRequest"></a>

## MaterializeRequest Objects

```python
class MaterializeRequest(BaseModel)
```

Request object for materializing feature views.

**Attributes**:

- `end_date` - The end date of the materialization window. Defaults to the current time.
- `feature_views` - A list of feature view names to materialize. If not provided, all feature views will be
  materialized.
- `start_date` - The start date of the materialization window. Defaults to None, which will use the start date of
  the feature view.

<a id="wyvern.feature_store.schemas.RequestEntityIdentifierObjects"></a>

## RequestEntityIdentifierObjects Objects

```python
class RequestEntityIdentifierObjects(BaseModel)
```

Request object for getting entity identifier objects.

**Attributes**:

- `request_ids` - A list of request IDs.
- `entity_identifiers` - A list of entity identifiers.
- `feature_names` - A list of feature names.

<a id="wyvern.feature_store.feature_server"></a>

# wyvern.feature_store.feature_server

<a id="wyvern.feature_store.feature_server.CRONJOB_INTERVAL_SECONDS"></a>

#### CRONJOB_INTERVAL_SECONDS

5 minutes

<a id="wyvern.feature_store.feature_server.CRONJOB_LOOKBACK_MINUTES"></a>

#### CRONJOB_LOOKBACK_MINUTES

12 mins

<a id="wyvern.feature_store.feature_server.generate_wyvern_store_app"></a>

#### generate_wyvern_store_app

```python
def generate_wyvern_store_app(path: str) -> FastAPI
```

Generate a FastAPI app for Wyvern feature store.

**Arguments**:

- `path` - Path to the feature store repo.

**Returns**:

FastAPI app.

<a id="wyvern.feature_store.feature_server.start_wyvern_store"></a>

#### start_wyvern_store

```python
def start_wyvern_store(path: str, host: str, port: int)
```

Start the Wyvern feature store.

**Arguments**:

- `path` - Path to the feature store repo.
- `host` - Host to run the feature store on.
- `port` - Port to run the feature store on.

<a id="wyvern.feature_store.historical_feature_util"></a>

# wyvern.feature_store.historical_feature_util

<a id="wyvern.feature_store.historical_feature_util.separate_real_time_features"></a>

#### separate_real_time_features

```python
def separate_real_time_features(
        full_feature_names: Optional[List[str]]
) -> Tuple[List[str], List[str]]
```

Given a list of full feature names, separate real-time features and other features.

**Arguments**:

- `full_feature_names` - a list of full feature names.

**Returns**:

Real time feature names and other feature names in two lists respectively.

<a id="wyvern.feature_store.historical_feature_util.build_historical_real_time_feature_requests"></a>

#### build_historical_real_time_feature_requests

```python
def build_historical_real_time_feature_requests(
    full_feature_names: List[str], request_ids: List[str],
    entities: Dict[str,
                   List[Any]]) -> Dict[str, RequestEntityIdentifierObjects]
```

Build historical real-time feature requests grouped by entity types so that we can process them in parallel.

**Arguments**:

- `full_feature_names` - a list of full feature names.
- `request_ids` - a list of request ids.
- `entities` - a dictionary of entity names and their values.

**Returns**:

A dictionary of entity types and their corresponding requests.

<a id="wyvern.feature_store.historical_feature_util.process_historical_real_time_features_requests"></a>

#### process_historical_real_time_features_requests

```python
def process_historical_real_time_features_requests(
    requests: Dict[str, RequestEntityIdentifierObjects]
) -> Dict[str, pd.DataFrame]
```

Given a dictionary of historical real-time feature requests, process them and return the results.

**Arguments**:

- `requests` - a dictionary of entity types and their corresponding requests.

**Returns**:

A dictionary of entity types and their corresponding results in pandas dataframes.

<a id="wyvern.feature_store.historical_feature_util.process_historical_real_time_features_request"></a>

#### process_historical_real_time_features_request

```python
def process_historical_real_time_features_request(
        entity_identifier_type: str, request: RequestEntityIdentifierObjects,
        context: SnowflakeConnection) -> pd.DataFrame
```

Given a historical real-time feature request, process it and return the results.

**Arguments**:

- `entity_identifier_type` - the entity type of the request. E.g. "product\_\_query"
- `request` - the request object.
- `context` - the snowflake connection context.

**Returns**:

The result in pandas dataframe.

<a id="wyvern.feature_store.historical_feature_util.group_realtime_features_by_entity_type"></a>

#### group_realtime_features_by_entity_type

```python
def group_realtime_features_by_entity_type(
        full_feature_names: List[str]) -> Dict[str, List[str]]
```

Given a list of feature names, group them by their entity_identifier_type

**Arguments**:

- `full_feature_names` - a list of full feature names.

**Returns**:

A dictionary of entity types and their corresponding feature names.

<a id="wyvern.feature_store.historical_feature_util.group_registry_features_by_entities"></a>

#### group_registry_features_by_entities

```python
def group_registry_features_by_entities(
        full_feature_names: List[str],
        store: FeatureStore) -> Dict[str, List[str]]
```

Given a list of feature names, group them by their entity name.

**Arguments**:

- `full_feature_names` - a list of full feature names.
- `store` - the feast feature store.

**Returns**:

A dictionary of entity names and their corresponding feature names.

<a id="wyvern.feature_store.historical_feature_util.build_historical_registry_feature_requests"></a>

#### build_historical_registry_feature_requests

```python
def build_historical_registry_feature_requests(
        store: FeatureStore, feature_names: List[str],
        entity_values: Dict[str, List[Any]],
        timestamps: List[datetime]) -> List[GetFeastHistoricalFeaturesRequest]
```

Build historical feature requests grouped by entity names so that we can process them in parallel.

**Arguments**:

- `store` - the feast feature store.
- `feature_names` - a list of feature names.
- `entity_values` - a dictionary of entity names and their values.
- `timestamps` - a list of timestamps for getting historical features at those timestamps.

**Returns**:

A list of historical feature requests.

<a id="wyvern.feature_store.historical_feature_util.process_historical_registry_features_requests"></a>

#### process_historical_registry_features_requests

```python
def process_historical_registry_features_requests(
        store: FeatureStore, requests: List[GetFeastHistoricalFeaturesRequest]
) -> List[pd.DataFrame]
```

Given a list of historical feature requests, process them and return the results

**Arguments**:

- `store` - the feast feature store.
- `requests` - a list of historical feature requests.

**Returns**:

A list of results in pandas dataframes.

<a id="wyvern.feature_store.historical_feature_util.process_historical_registry_features_request"></a>

#### process_historical_registry_features_request

```python
def process_historical_registry_features_request(
        store: FeatureStore,
        request: GetFeastHistoricalFeaturesRequest) -> pd.DataFrame
```

Given a historical feature request, process it and return the results

**Arguments**:

- `store` - the feast feature store.
- `request` - a historical feature request.

**Returns**:

The result in pandas dataframe.

<a id="wyvern.helper.sort"></a>

# wyvern.helper.sort

<a id="wyvern.helper.sort.SortEnum"></a>

## SortEnum Objects

```python
class SortEnum(str, Enum)
```

Enum for sort order.

<a id="wyvern.helper.sort.Sort"></a>

## Sort Objects

```python
class Sort(BaseModel)
```

Sort class for sorting the results.

**Attributes**:

- `sort_key` - The key to sort on.
- `sort_field` - The field to sort on.
- `sort_order` - The order to sort on. Defaults to desc.

<a id="wyvern.helper"></a>

# wyvern.helper

<a id="wyvern.entities.feature_entity_helpers"></a>

# wyvern.entities.feature_entity_helpers

<a id="wyvern.entities.feature_entity_helpers.feature_map_join"></a>

#### feature_map_join

```python
def feature_map_join(*feature_maps: FeatureMap) -> FeatureMap
```

Joins multiple feature maps into a single feature map. Used to join feature maps from different sources.

<a id="wyvern.entities.feature_entity_helpers.feature_map_create"></a>

#### feature_map_create

```python
def feature_map_create(*feature_data: Optional[FeatureData]) -> FeatureMap
```

Creates a feature map from a list of feature data. Used to create feature maps from different sources.

<a id="wyvern.entities.index_entities"></a>

# wyvern.entities.index_entities

<a id="wyvern.entities.identifier_entities"></a>

# wyvern.entities.identifier_entities

<a id="wyvern.entities.identifier_entities.WyvernDataModel"></a>

## WyvernDataModel Objects

```python
class WyvernDataModel(BaseModel)
```

WyvernDataModel is a base class for all data models that could be hydrated from Wyvern Index.

**Attributes**:

- `_all_entities` - a list of all the entities under the tree
- `_all_identifiers` - a list of all the identifiers under the tree

<a id="wyvern.entities.identifier_entities.WyvernDataModel.index_fields"></a>

#### index_fields

```python
def index_fields() -> List[str]
```

This method returns a list of fields that contains indexable data

<a id="wyvern.entities.identifier_entities.WyvernDataModel.get_all_entities"></a>

#### get_all_entities

```python
def get_all_entities(cached: bool = True) -> List[WyvernEntity]
```

This method returns all of the entities associated with subclasses of this

If cached is True, all the nodes under the tree will be cached

<a id="wyvern.entities.identifier_entities.WyvernDataModel.get_all_identifiers"></a>

#### get_all_identifiers

```python
def get_all_identifiers(cached: bool = True) -> List[Identifier]
```

This method generally returns all of the identifiers associated with subclasses of this

Example: You create a QueryProductEntity with query="test" and product_id="1234"
It subclasses QueryEntity and ProductEntity, which both have an identifier
This method will return a list of both of those identifiers

Example: You create a ProductSearchRankingRequest with
query="test", candidates=["1234", ...], user="u_1234"
This method will return the user and query identifier
It will also return the identifiers for each candidate (thanks to the implementation in CandidateEntity)

Note: While this checks for `WyvernEntity` -- a `WyvernDataModel` can have many
entities within it, it itself may not be an entity

<a id="wyvern.entities.identifier_entities.WyvernDataModel.nested_hydration"></a>

#### nested_hydration

```python
def nested_hydration() -> Dict[str, str]
```

A dictionary that maps the entity id field name to the nested entity field name

TODO: [SHU] replace this mapping by introducing `class WyvernField(pydantic.Field)`
to represent the "entity ide field", which will reference to the nested entity field name

<a id="wyvern.entities.identifier_entities.WyvernEntity"></a>

## WyvernEntity Objects

```python
class WyvernEntity(WyvernDataModel)
```

WyvernEntity is a base class for all entities that have primary identifier
TODO:
we want to design a way to so that 1. the primary key of the entity could map to the name of the entity 2. it's easy to define the relation

example:
have a @wyvern_entity decorator that could be used to define the primary key name
and identifier type
@wyvenr_entity(key="product_id", type="product")

<a id="wyvern.entities.identifier_entities.WyvernEntity.identifier"></a>

#### identifier

```python
@property
def identifier() -> Identifier
```

This method returns the identifier for this entity

<a id="wyvern.entities.identifier_entities.WyvernEntity.load_fields"></a>

#### load_fields

```python
def load_fields(data: Dict[str, Any]) -> None
```

This method load the entity with the given data.
The return data is the nested entities that need to be further hydrated

For example:
if a Product contains these two fields: `brand_id: Optional[str]` and `brand: Optional[Brand]`,
as the hydrated entity. We fetch the brand_id for the product from Wyvern Index,
as the first hydration step for Product entity, then we fetch brand entity from Wyvern Index,
as the second hydration step

<a id="wyvern.entities.identifier_entities.QueryEntity"></a>

## QueryEntity Objects

```python
class QueryEntity(WyvernEntity)
```

QueryEntity is a base class for all entities that have query as an identifier.

**Attributes**:

- `query` - the query string

<a id="wyvern.entities.identifier_entities.QueryEntity.generate_identifier"></a>

#### generate_identifier

```python
def generate_identifier() -> Identifier
```

This method returns the identifier for this entity.

**Returns**:

- `Identifier` - the identifier for this entity with identifier_type=SimpleIdentifierType.QUERY.

<a id="wyvern.entities.identifier_entities.ProductEntity"></a>

## ProductEntity Objects

```python
class ProductEntity(WyvernEntity)
```

ProductEntity is a base class for all entities that have product_id as an identifier.

**Attributes**:

- `product_id` - the product id

<a id="wyvern.entities.identifier_entities.ProductEntity.generate_identifier"></a>

#### generate_identifier

```python
def generate_identifier() -> Identifier
```

This method returns the identifier for this entity.

**Returns**:

- `Identifier` - the identifier for this entity with identifier_type=SimpleIdentifierType.PRODUCT.

<a id="wyvern.entities.identifier_entities.UserEntity"></a>

## UserEntity Objects

```python
class UserEntity(WyvernEntity)
```

UserEntity is a base class for all entities that have user_id as an identifier.

**Attributes**:

- `user_id` - the user id

<a id="wyvern.entities.identifier_entities.UserEntity.generate_identifier"></a>

#### generate_identifier

```python
def generate_identifier() -> Identifier
```

This method returns the identifier for this entity.

**Returns**:

- `Identifier` - the identifier for this entity with identifier_type=SimpleIdentifierType.USER.

<a id="wyvern.entities.request"></a>

# wyvern.entities.request

<a id="wyvern.entities.request.BaseWyvernRequest"></a>

## BaseWyvernRequest Objects

```python
class BaseWyvernRequest(WyvernDataModel)
```

Base class for all Wyvern requests. This class is used to generate an identifier for the request.

**Attributes**:

- `request_id` - The request id.
- `include_events` - Whether to include events in the response.

<a id="wyvern.entities.request.BaseWyvernRequest.generate_identifier"></a>

#### generate_identifier

```python
def generate_identifier() -> Identifier
```

Generates an identifier for the request.

**Returns**:

- `Identifier` - The identifier for the request. The identifier type is "request".

<a id="wyvern.entities"></a>

# wyvern.entities

<a id="wyvern.entities.feature_entities"></a>

# wyvern.entities.feature_entities

<a id="wyvern.entities.feature_entities.FeatureData"></a>

## FeatureData Objects

```python
class FeatureData(BaseModel)
```

A class to represent the features of an entity.

**Attributes**:

- `identifier` - The identifier of the entity.
- `features` - A dictionary of feature names to feature values.

<a id="wyvern.entities.feature_entities.FeatureMap"></a>

## FeatureMap Objects

```python
class FeatureMap(BaseModel)
```

A class to represent a map of identifiers to feature data.

TODO (kerem): Fix the data duplication between this class and the FeatureData class. The identifier field in the
FeatureData class is redundant.

<a id="wyvern.entities.feature_entities.build_empty_feature_map"></a>

#### build_empty_feature_map

```python
def build_empty_feature_map(identifiers: List[Identifier],
                            feature_names: List[str]) -> FeatureMap
```

Builds an empty feature map with the given identifiers and feature names.

<a id="wyvern.entities.identifier"></a>

# wyvern.entities.identifier

<a id="wyvern.entities.identifier.SimpleIdentifierType"></a>

## SimpleIdentifierType Objects

```python
class SimpleIdentifierType(str, Enum)
```

Simple identifier types are those that are not composite.

<a id="wyvern.entities.identifier.composite"></a>

#### composite

```python
def composite(primary_identifier_type: SimpleIdentifierType,
              secondary_identifier_type: SimpleIdentifierType) -> str
```

Composite identifier types are those that are composite. For example, a product with id p_1234 and type "product"
a user with id u_1234 and type "user" would have a composite identifier of "p_1234:u_1234", and a composite
identifier_type of "product:user". This is useful for indexing and searching for composite entities.

<a id="wyvern.entities.identifier.CompositeIdentifierType"></a>

## CompositeIdentifierType Objects

```python
class CompositeIdentifierType(str, Enum)
```

Composite identifier types are those that are composite. For example, a composite identifier type of
"product:user" would be a composite identifier type for a product and a user. This is useful for indexing and
searching for composite entities.

<a id="wyvern.entities.identifier.Identifier"></a>

## Identifier Objects

```python
class Identifier(BaseModel)
```

Identifiers exist to represent a unique entity through their unique id and their type
For example: a product with id p_1234 and type "product" or a user with id u_1234 and type "user"

Composite identifiers are also possible, for example:
a product with id p_1234 and type "product"
a user with id u_1234 and type "user"

    The composite identifier would be "p_1234:u_1234",
        and the composite identifier_type would be "product:user"

<a id="wyvern.entities.identifier.CompositeIdentifier"></a>

## CompositeIdentifier Objects

```python
class CompositeIdentifier(Identifier)
```

Composite identifiers exist to represent a unique entity through their unique id and their type. At most, they
can have two identifiers and two identifier types. For example:
a product with id p_1234 and type "product"
a user with id u_1234 and type "user"

    The composite identifier would be "p_1234:u_1234", and the composite identifier_type would be "product:user".

<a id="wyvern.entities.candidate_entities"></a>

# wyvern.entities.candidate_entities

<a id="wyvern.entities.candidate_entities.ScoredCandidate"></a>

## ScoredCandidate Objects

```python
class ScoredCandidate(GenericModel, Generic[GENERALIZED_WYVERN_ENTITY])
```

A candidate entity with a score.

**Attributes**:

- `entity` - The candidate entity.
- `score` - The score of the candidate entity. Defaults to 0.0.

<a id="wyvern.entities.candidate_entities.CandidateSetEntity"></a>

## CandidateSetEntity Objects

```python
class CandidateSetEntity(WyvernDataModel, GenericModel,
                         Generic[GENERALIZED_WYVERN_ENTITY])
```

A set of candidate entities. This is a generic model that can be used to represent a set of candidate entities.

**Attributes**:

- `candidates` - The list of candidate entities.

<a id="examples"></a>

# examples

<a id="examples.feature_store_main"></a>

# examples.feature_store_main

<a id="examples.feature_store_main.run"></a>

#### run

```python
@wyvern_cli_app.command()
def run(host: str = "127.0.0.1", port: int = 8000) -> None
```

Run your wyvern service

<a id="examples.example_business_logic"></a>

# examples.example_business_logic

<a id="examples.example_business_logic.sample_product_query_ranking_request"></a>

#### sample_product_query_ranking_request

```python
async def sample_product_query_ranking_request() -> None
```

How to run this: `python wyvern/examples/example_business_logic.py`

Json representation of the request:

```
{
    "request_id": "rrr",
    "query": "candle",
    "candidates": [
        {"product_id": "1", "product_name": "scented candle"},
        {"product_id": "2", "product_name": "hot candle"},
        {"product_id": "3", "product_name": "pumpkin candle"},
        {"product_id": "4", "product_name": "unrelated item"},
        {"product_id": "5", "product_name": "candle holder accessory"},
        {"product_id": "6", "product_name": "earwax holder"},
        {"product_id": "7", "product_name": "wax seal"}
   ],
}
```

<a id="examples.real_time_features_main"></a>

# examples.real_time_features_main

<a id="examples.real_time_features_main.run"></a>

#### run

```python
@wyvern_cli_app.command()
def run(host: str = "127.0.0.1", port: int = 8000) -> None
```

Run your wyvern service
