# RemoteGraph

# RemoteGraph[¶](#remotegraph "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `RemoteGraph` | The `RemoteGraph` class is a client implementation for calling remote |
## RemoteGraph [¶](#langgraph.pregel.remote.RemoteGraph "Permanent link")
Bases: `PregelProtocol`
The `RemoteGraph` class is a client implementation for calling remote
APIs that implement the LangGraph Server API specification.
For example, the `RemoteGraph` class can be used to call APIs from deployments
on LangGraph Platform.
`RemoteGraph` behaves the same way as a `Graph` and can be used directly as
a node in another `Graph`.
Methods:
| Name | Description |
| --- | --- |
| `__init__` | Specify `url`, `api_key`, and/or `headers` to create default sync and async clients. |
| `get_graph` | Get graph by graph name. |
| `aget_graph` | Get graph by graph name. |
| `get_state` | Get the state of a thread. |
| `aget_state` | Get the state of a thread. |
| `get_state_history` | Get the state history of a thread. |
| `aget_state_history` | Get the state history of a thread. |
| `update_state` | Update the state of a thread. |
| `aupdate_state` | Update the state of a thread. |
| `stream` | Create a run and stream the results. |
| `astream` | Create a run and stream the results. |
| `invoke` | Create a run, wait until it finishes and return the final state. |
| `ainvoke` | Create a run, wait until it finishes and return the final state. |
| `get_name` | Get the name of the Runnable. |
| `get_input_schema` | Get a pydantic model that can be used to validate input to the Runnable. |
| `get_input_jsonschema` | Get a JSON schema that represents the input to the Runnable. |
| `get_output_schema` | Get a pydantic model that can be used to validate output to the Runnable. |
| `get_output_jsonschema` | Get a JSON schema that represents the output of the Runnable. |
| `config_schema` | The type of config this Runnable accepts specified as a pydantic model. |
| `get_config_jsonschema` | Get a JSON schema that represents the config of the Runnable. |
| `get_prompts` | Return a list of prompts used by this Runnable. |
| `__or__` | Compose this Runnable with another object to create a RunnableSequence. |
| `__ror__` | Compose this Runnable with another object to create a RunnableSequence. |
| `pipe` | Compose this Runnable with Runnable-like objects to make a RunnableSequence. |
| `pick` | Pick keys from the output dict of this Runnable. |
| `assign` | Assigns new fields to the dict output of this Runnable. |
| `batch` | Default implementation runs invoke in parallel using a thread pool executor. |
| `batch_as_completed` | Run invoke in parallel on a list of inputs. |
| `abatch` | Default implementation runs ainvoke in parallel using asyncio.gather. |
| `abatch_as_completed` | Run ainvoke in parallel on a list of inputs. |
| `astream_log` | Stream all output from a Runnable, as reported to the callback system. |
| `transform` | Default implementation of transform, which buffers input and calls astream. |
| `atransform` | Default implementation of atransform, which buffers input and calls astream. |
| `bind` | Bind arguments to a Runnable, returning a new Runnable. |
| `with_listeners` | Bind lifecycle listeners to a Runnable, returning a new Runnable. |
| `with_alisteners` | Bind async lifecycle listeners to a Runnable, returning a new Runnable. |
| `with_types` | Bind input and output types to a Runnable, returning a new Runnable. |
| `with_retry` | Create a new Runnable that retries the original Runnable on exceptions. |
| `map` | Return a new Runnable that maps a list of inputs to a list of outputs. |
| `with_fallbacks` | Add fallbacks to a Runnable, returning a new Runnable. |
| `as_tool` | Create a BaseTool from a Runnable. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `InputType` | `type[Input]` | The type of input this Runnable accepts specified as a type annotation. |
| `OutputType` | `type[Output]` | The type of output this Runnable produces specified as a type annotation. |
| `input_schema` | `type[BaseModel]` | The type of input this Runnable accepts specified as a pydantic model. |
| `output_schema` | `type[BaseModel]` | The type of output this Runnable produces specified as a pydantic model. |
| `config_specs` | `list[ConfigurableFieldSpec]` | List configurable fields for this Runnable. |
### InputType `property` [¶](#langgraph.pregel.remote.RemoteGraph.InputType "Permanent link")
```
InputType: type[Input]
```
The type of input this Runnable accepts specified as a type annotation.
### OutputType `property` [¶](#langgraph.pregel.remote.RemoteGraph.OutputType "Permanent link")
```
OutputType: type[Output]
```
The type of output this Runnable produces specified as a type annotation.
### input\_schema `property` [¶](#langgraph.pregel.remote.RemoteGraph.input_schema "Permanent link")
```
input_schema: type[BaseModel]
```
The type of input this Runnable accepts specified as a pydantic model.
### output\_schema `property` [¶](#langgraph.pregel.remote.RemoteGraph.output_schema "Permanent link")
```
output_schema: type[BaseModel]
```
The type of output this Runnable produces specified as a pydantic model.
### config\_specs `property` [¶](#langgraph.pregel.remote.RemoteGraph.config_specs "Permanent link")
```
config_specs: list[ConfigurableFieldSpec]
```
List configurable fields for this Runnable.
### \_\_init\_\_ [¶](#langgraph.pregel.remote.RemoteGraph.__init__ "Permanent link")
```
__init__(
    assistant_id: str,
    /,
    *,
    url: str | None = None,
    api_key: str | None = None,
    headers: dict[str, str] | None = None,
    client: LangGraphClient | None = None,
    sync_client: SyncLangGraphClient | None = None,
    config: RunnableConfig | None = None,
    name: str | None = None,
    distributed_tracing: bool = False,
)
```
Specify `url`, `api_key`, and/or `headers` to create default sync and async clients.
If `client` or `sync_client` are provided, they will be used instead of the default clients.
See `LangGraphClient` and `SyncLangGraphClient` for details on the default clients. At least
one of `url`, `client`, or `sync_client` must be provided.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `assistant_id` | `str` | The assistant ID or graph name of the remote graph to use. | *required* |
| `url` | `str | None` | The URL of the remote API. | `None` |
| `api_key` | `str | None` | The API key to use for authentication. If not provided, it will be read from the environment (`LANGGRAPH_API_KEY`, `LANGSMITH_API_KEY`, or `LANGCHAIN_API_KEY`). | `None` |
| `headers` | `dict[str, str] | None` | Additional headers to include in the requests. | `None` |
| `client` | `LangGraphClient | None` | A `LangGraphClient` instance to use instead of creating a default client. | `None` |
| `sync_client` | `SyncLangGraphClient | None` | A `SyncLangGraphClient` instance to use instead of creating a default client. | `None` |
| `config` | `RunnableConfig | None` | An optional `RunnableConfig` instance with additional configuration. | `None` |
| `name` | `str | None` | Human-readable name to attach to the RemoteGraph instance. This is useful for adding `RemoteGraph` as a subgraph via `graph.add_node(remote_graph)`. If not provided, defaults to the assistant ID. | `None` |
| `distributed_tracing` | `bool` | Whether to enable sending LangSmith distributed tracing headers. | `False` |
### get\_graph [¶](#langgraph.pregel.remote.RemoteGraph.get_graph "Permanent link")
```
get_graph(
    config: RunnableConfig | None = None,
    *,
    xray: int | bool = False,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> Graph
```
Get graph by graph name.
This method calls `GET /assistants/{assistant_id}/graph`.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | This parameter is not used. | `None` |
| `xray` | `int | bool` | Include graph representation of subgraphs. If an integer value is provided, only subgraphs with a depth less than or equal to the value will be included. | `False` |
Returns:
| Type | Description |
| --- | --- |
| `Graph` | The graph information for the assistant in JSON format. |
### aget\_graph `async` [¶](#langgraph.pregel.remote.RemoteGraph.aget_graph "Permanent link")
```
aget_graph(
    config: RunnableConfig | None = None,
    *,
    xray: int | bool = False,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> Graph
```
Get graph by graph name.
This method calls `GET /assistants/{assistant_id}/graph`.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | This parameter is not used. | `None` |
| `xray` | `int | bool` | Include graph representation of subgraphs. If an integer value is provided, only subgraphs with a depth less than or equal to the value will be included. | `False` |
Returns:
| Type | Description |
| --- | --- |
| `Graph` | The graph information for the assistant in JSON format. |
### get\_state [¶](#langgraph.pregel.remote.RemoteGraph.get_state "Permanent link")
```
get_state(
    config: RunnableConfig,
    *,
    subgraphs: bool = False,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> StateSnapshot
```
Get the state of a thread.
This method calls `POST /threads/{thread_id}/state/checkpoint` if a
checkpoint is specified in the config or `GET /threads/{thread_id}/state`
if no checkpoint is specified.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | A `RunnableConfig` that includes `thread_id` in the `configurable` field. | *required* |
| `subgraphs` | `bool` | Include subgraphs in the state. | `False` |
| `headers` | `dict[str, str] | None` | Optional custom headers to include with the request. | `None` |
| `params` | `QueryParamTypes | None` | Optional query parameters to include with the request. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `StateSnapshot` | The latest state of the thread. |
### aget\_state `async` [¶](#langgraph.pregel.remote.RemoteGraph.aget_state "Permanent link")
```
aget_state(
    config: RunnableConfig,
    *,
    subgraphs: bool = False,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> StateSnapshot
```
Get the state of a thread.
This method calls `POST /threads/{thread_id}/state/checkpoint` if a
checkpoint is specified in the config or `GET /threads/{thread_id}/state`
if no checkpoint is specified.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | A `RunnableConfig` that includes `thread_id` in the `configurable` field. | *required* |
| `subgraphs` | `bool` | Include subgraphs in the state. | `False` |
| `headers` | `dict[str, str] | None` | Optional custom headers to include with the request. | `None` |
| `params` | `QueryParamTypes | None` | Optional query parameters to include with the request. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `StateSnapshot` | The latest state of the thread. |
### get\_state\_history [¶](#langgraph.pregel.remote.RemoteGraph.get_state_history "Permanent link")
```
get_state_history(
    config: RunnableConfig,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> Iterator[StateSnapshot]
```
Get the state history of a thread.
This method calls `POST /threads/{thread_id}/history`.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | A `RunnableConfig` that includes `thread_id` in the `configurable` field. | *required* |
| `filter` | `dict[str, Any] | None` | Metadata to filter on. | `None` |
| `before` | `RunnableConfig | None` | A `RunnableConfig` that includes checkpoint metadata. | `None` |
| `limit` | `int | None` | Max number of states to return. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Iterator[StateSnapshot]` | States of the thread. |
### aget\_state\_history `async` [¶](#langgraph.pregel.remote.RemoteGraph.aget_state_history "Permanent link")
```
aget_state_history(
    config: RunnableConfig,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> AsyncIterator[StateSnapshot]
```
Get the state history of a thread.
This method calls `POST /threads/{thread_id}/history`.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | A `RunnableConfig` that includes `thread_id` in the `configurable` field. | *required* |
| `filter` | `dict[str, Any] | None` | Metadata to filter on. | `None` |
| `before` | `RunnableConfig | None` | A `RunnableConfig` that includes checkpoint metadata. | `None` |
| `limit` | `int | None` | Max number of states to return. | `None` |
| `headers` | `dict[str, str] | None` | Optional custom headers to include with the request. | `None` |
| `params` | `QueryParamTypes | None` | Optional query parameters to include with the request. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `AsyncIterator[StateSnapshot]` | States of the thread. |
### update\_state [¶](#langgraph.pregel.remote.RemoteGraph.update_state "Permanent link")
```
update_state(
    config: RunnableConfig,
    values: dict[str, Any] | Any | None,
    as_node: str | None = None,
    *,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> RunnableConfig
```
Update the state of a thread.
This method calls `POST /threads/{thread_id}/state`.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | A `RunnableConfig` that includes `thread_id` in the `configurable` field. | *required* |
| `values` | `dict[str, Any] | Any | None` | Values to update to the state. | *required* |
| `as_node` | `str | None` | Update the state as if this node had just executed. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `RunnableConfig` | `RunnableConfig` for the updated thread. |
### aupdate\_state `async` [¶](#langgraph.pregel.remote.RemoteGraph.aupdate_state "Permanent link")
```
aupdate_state(
    config: RunnableConfig,
    values: dict[str, Any] | Any | None,
    as_node: str | None = None,
    *,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None
) -> RunnableConfig
```
Update the state of a thread.
This method calls `POST /threads/{thread_id}/state`.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | A `RunnableConfig` that includes `thread_id` in the `configurable` field. | *required* |
| `values` | `dict[str, Any] | Any | None` | Values to update to the state. | *required* |
| `as_node` | `str | None` | Update the state as if this node had just executed. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `RunnableConfig` | `RunnableConfig` for the updated thread. |
### stream [¶](#langgraph.pregel.remote.RemoteGraph.stream "Permanent link")
```
stream(
    input: dict[str, Any] | Any,
    config: RunnableConfig | None = None,
    *,
    stream_mode: (
        StreamMode | list[StreamMode] | None
    ) = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    subgraphs: bool = False,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None,
    **kwargs: Any
) -> Iterator[dict[str, Any] | Any]
```
Create a run and stream the results.
This method calls `POST /threads/{thread_id}/runs/stream` if a `thread_id`
is speciffed in the `configurable` field of the config or
`POST /runs/stream` otherwise.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `dict[str, Any] | Any` | Input to the graph. | *required* |
| `config` | `RunnableConfig | None` | A `RunnableConfig` for graph invocation. | `None` |
| `stream_mode` | `StreamMode | list[StreamMode] | None` | Stream mode(s) to use. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Interrupt the graph before these nodes. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Interrupt the graph after these nodes. | `None` |
| `subgraphs` | `bool` | Stream from subgraphs. | `False` |
| `headers` | `dict[str, str] | None` | Additional headers to pass to the request. | `None` |
| `**kwargs` | `Any` | Additional params to pass to client.runs.stream. | `{}` |
Yields:
| Type | Description |
| --- | --- |
| `dict[str, Any] | Any` | The output of the graph. |
### astream `async` [¶](#langgraph.pregel.remote.RemoteGraph.astream "Permanent link")
```
astream(
    input: dict[str, Any] | Any,
    config: RunnableConfig | None = None,
    *,
    stream_mode: (
        StreamMode | list[StreamMode] | None
    ) = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    subgraphs: bool = False,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None,
    **kwargs: Any
) -> AsyncIterator[dict[str, Any] | Any]
```
Create a run and stream the results.
This method calls `POST /threads/{thread_id}/runs/stream` if a `thread_id`
is speciffed in the `configurable` field of the config or
`POST /runs/stream` otherwise.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `dict[str, Any] | Any` | Input to the graph. | *required* |
| `config` | `RunnableConfig | None` | A `RunnableConfig` for graph invocation. | `None` |
| `stream_mode` | `StreamMode | list[StreamMode] | None` | Stream mode(s) to use. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Interrupt the graph before these nodes. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Interrupt the graph after these nodes. | `None` |
| `subgraphs` | `bool` | Stream from subgraphs. | `False` |
| `headers` | `dict[str, str] | None` | Additional headers to pass to the request. | `None` |
| `**kwargs` | `Any` | Additional params to pass to client.runs.stream. | `{}` |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[dict[str, Any] | Any]` | The output of the graph. |
### invoke [¶](#langgraph.pregel.remote.RemoteGraph.invoke "Permanent link")
```
invoke(
    input: dict[str, Any] | Any,
    config: RunnableConfig | None = None,
    *,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None,
    **kwargs: Any
) -> dict[str, Any] | Any
```
Create a run, wait until it finishes and return the final state.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `dict[str, Any] | Any` | Input to the graph. | *required* |
| `config` | `RunnableConfig | None` | A `RunnableConfig` for graph invocation. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Interrupt the graph before these nodes. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Interrupt the graph after these nodes. | `None` |
| `headers` | `dict[str, str] | None` | Additional headers to pass to the request. | `None` |
| `**kwargs` | `Any` | Additional params to pass to RemoteGraph.stream. | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any] | Any` | The output of the graph. |
### ainvoke `async` [¶](#langgraph.pregel.remote.RemoteGraph.ainvoke "Permanent link")
```
ainvoke(
    input: dict[str, Any] | Any,
    config: RunnableConfig | None = None,
    *,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    headers: dict[str, str] | None = None,
    params: QueryParamTypes | None = None,
    **kwargs: Any
) -> dict[str, Any] | Any
```
Create a run, wait until it finishes and return the final state.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `dict[str, Any] | Any` | Input to the graph. | *required* |
| `config` | `RunnableConfig | None` | A `RunnableConfig` for graph invocation. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Interrupt the graph before these nodes. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Interrupt the graph after these nodes. | `None` |
| `headers` | `dict[str, str] | None` | Additional headers to pass to the request. | `None` |
| `**kwargs` | `Any` | Additional params to pass to RemoteGraph.astream. | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any] | Any` | The output of the graph. |
### get\_name [¶](#langgraph.pregel.remote.RemoteGraph.get_name "Permanent link")
```
get_name(
    suffix: Optional[str] = None,
    *,
    name: Optional[str] = None
) -> str
```
Get the name of the Runnable.
### get\_input\_schema [¶](#langgraph.pregel.remote.RemoteGraph.get_input_schema "Permanent link")
```
get_input_schema(
    config: Optional[RunnableConfig] = None,
) -> type[BaseModel]
```
Get a pydantic model that can be used to validate input to the Runnable.
Runnables that leverage the configurable\_fields and configurable\_alternatives
methods will have a dynamic input schema that depends on which
configuration the Runnable is invoked with.
This method allows to get an input schema for a specific configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `Optional[RunnableConfig]` | A config to use when generating the schema. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `type[BaseModel]` | A pydantic model that can be used to validate input. |
### get\_input\_jsonschema [¶](#langgraph.pregel.remote.RemoteGraph.get_input_jsonschema "Permanent link")
```
get_input_jsonschema(
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]
```
Get a JSON schema that represents the input to the Runnable.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `Optional[RunnableConfig]` | A config to use when generating the schema. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any]` | A JSON schema that represents the input to the Runnable. |
Example:
```
.. code-block:: python
    from langchain_core.runnables import RunnableLambda
    def add_one(x: int) -> int:
        return x + 1
    runnable = RunnableLambda(add_one)
    print(runnable.get_input_jsonschema())
```
.. versionadded:: 0.3.0
### get\_output\_schema [¶](#langgraph.pregel.remote.RemoteGraph.get_output_schema "Permanent link")
```
get_output_schema(
    config: Optional[RunnableConfig] = None,
) -> type[BaseModel]
```
Get a pydantic model that can be used to validate output to the Runnable.
Runnables that leverage the configurable\_fields and configurable\_alternatives
methods will have a dynamic output schema that depends on which
configuration the Runnable is invoked with.
This method allows to get an output schema for a specific configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `Optional[RunnableConfig]` | A config to use when generating the schema. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `type[BaseModel]` | A pydantic model that can be used to validate output. |
### get\_output\_jsonschema [¶](#langgraph.pregel.remote.RemoteGraph.get_output_jsonschema "Permanent link")
```
get_output_jsonschema(
    config: Optional[RunnableConfig] = None,
) -> dict[str, Any]
```
Get a JSON schema that represents the output of the Runnable.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `Optional[RunnableConfig]` | A config to use when generating the schema. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any]` | A JSON schema that represents the output of the Runnable. |
Example:
```
.. code-block:: python
    from langchain_core.runnables import RunnableLambda
    def add_one(x: int) -> int:
        return x + 1
    runnable = RunnableLambda(add_one)
    print(runnable.get_output_jsonschema())
```
.. versionadded:: 0.3.0
### config\_schema [¶](#langgraph.pregel.remote.RemoteGraph.config_schema "Permanent link")
```
config_schema(
    *, include: Optional[Sequence[str]] = None
) -> type[BaseModel]
```
The type of config this Runnable accepts specified as a pydantic model.
To mark a field as configurable, see the `configurable_fields`
and `configurable_alternatives` methods.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `include` | `Optional[Sequence[str]]` | A list of fields to include in the config schema. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `type[BaseModel]` | A pydantic model that can be used to validate config. |
### get\_config\_jsonschema [¶](#langgraph.pregel.remote.RemoteGraph.get_config_jsonschema "Permanent link")
```
get_config_jsonschema(
    *, include: Optional[Sequence[str]] = None
) -> dict[str, Any]
```
Get a JSON schema that represents the config of the Runnable.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `include` | `Optional[Sequence[str]]` | A list of fields to include in the config schema. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any]` | A JSON schema that represents the config of the Runnable. |
.. versionadded:: 0.3.0
### get\_prompts [¶](#langgraph.pregel.remote.RemoteGraph.get_prompts "Permanent link")
```
get_prompts(
    config: Optional[RunnableConfig] = None,
) -> list[BasePromptTemplate]
```
Return a list of prompts used by this Runnable.
### \_\_or\_\_ [¶](#langgraph.pregel.remote.RemoteGraph.__or__ "Permanent link")
```
__or__(
    other: Union[
        Runnable[Any, Other],
        Callable[[Iterator[Any]], Iterator[Other]],
        Callable[
            [AsyncIterator[Any]], AsyncIterator[Other]
        ],
        Callable[[Any], Other],
        Mapping[
            str,
            Union[
                Runnable[Any, Other],
                Callable[[Any], Other],
                Any,
            ],
        ],
    ],
) -> RunnableSerializable[Input, Other]
```
Compose this Runnable with another object to create a RunnableSequence.
### \_\_ror\_\_ [¶](#langgraph.pregel.remote.RemoteGraph.__ror__ "Permanent link")
```
__ror__(
    other: Union[
        Runnable[Other, Any],
        Callable[[Iterator[Other]], Iterator[Any]],
        Callable[
            [AsyncIterator[Other]], AsyncIterator[Any]
        ],
        Callable[[Other], Any],
        Mapping[
            str,
            Union[
                Runnable[Other, Any],
                Callable[[Other], Any],
                Any,
            ],
        ],
    ],
) -> RunnableSerializable[Other, Output]
```
Compose this Runnable with another object to create a RunnableSequence.
### pipe [¶](#langgraph.pregel.remote.RemoteGraph.pipe "Permanent link")
```
pipe(
    *others: Union[
        Runnable[Any, Other], Callable[[Any], Other]
    ],
    name: Optional[str] = None
) -> RunnableSerializable[Input, Other]
```
Compose this Runnable with Runnable-like objects to make a RunnableSequence.
Equivalent to `RunnableSequence(self, *others)` or `self | others[0] | ...`
Example
.. code-block:: python
```
from langchain_core.runnables import RunnableLambda
def add_one(x: int) -> int:
    return x + 1
def mul_two(x: int) -> int:
    return x * 2
runnable_1 = RunnableLambda(add_one)
runnable_2 = RunnableLambda(mul_two)
sequence = runnable_1.pipe(runnable_2)
# Or equivalently:
# sequence = runnable_1 | runnable_2
# sequence = RunnableSequence(first=runnable_1, last=runnable_2)
sequence.invoke(1)
await sequence.ainvoke(1)
# -> 4
sequence.batch([1, 2, 3])
await sequence.abatch([1, 2, 3])
# -> [4, 6, 8]
```
### pick [¶](#langgraph.pregel.remote.RemoteGraph.pick "Permanent link")
```
pick(
    keys: Union[str, list[str]],
) -> RunnableSerializable[Any, Any]
```
Pick keys from the output dict of this Runnable.
Pick single key
.. code-block:: python
```
import json
from langchain_core.runnables import RunnableLambda, RunnableMap
as_str = RunnableLambda(str)
as_json = RunnableLambda(json.loads)
chain = RunnableMap(str=as_str, json=as_json)
chain.invoke("[1, 2, 3]")
# -> {"str": "[1, 2, 3]", "json": [1, 2, 3]}
json_only_chain = chain.pick("json")
json_only_chain.invoke("[1, 2, 3]")
# -> [1, 2, 3]
```
Pick list of keys
.. code-block:: python
```
from typing import Any
import json
from langchain_core.runnables import RunnableLambda, RunnableMap
as_str = RunnableLambda(str)
as_json = RunnableLambda(json.loads)
def as_bytes(x: Any) -> bytes:
    return bytes(x, "utf-8")
chain = RunnableMap(
    str=as_str,
    json=as_json,
    bytes=RunnableLambda(as_bytes)
)
chain.invoke("[1, 2, 3]")
# -> {"str": "[1, 2, 3]", "json": [1, 2, 3], "bytes": b"[1, 2, 3]"}
json_and_bytes_chain = chain.pick(["json", "bytes"])
json_and_bytes_chain.invoke("[1, 2, 3]")
# -> {"json": [1, 2, 3], "bytes": b"[1, 2, 3]"}
```
### assign [¶](#langgraph.pregel.remote.RemoteGraph.assign "Permanent link")
```
assign(
    **kwargs: Union[
        Runnable[dict[str, Any], Any],
        Callable[[dict[str, Any]], Any],
        Mapping[
            str,
            Union[
                Runnable[dict[str, Any], Any],
                Callable[[dict[str, Any]], Any],
            ],
        ],
    ],
) -> RunnableSerializable[Any, Any]
```
Assigns new fields to the dict output of this Runnable.
Returns a new Runnable.
.. code-block:: python
```
from langchain_community.llms.fake import FakeStreamingListLLM
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import SystemMessagePromptTemplate
from langchain_core.runnables import Runnable
from operator import itemgetter
prompt = (
    SystemMessagePromptTemplate.from_template("You are a nice assistant.")
    + "{question}"
)
llm = FakeStreamingListLLM(responses=["foo-lish"])
chain: Runnable = prompt | llm | {"str": StrOutputParser()}
chain_with_assign = chain.assign(hello=itemgetter("str") | llm)
print(chain_with_assign.input_schema.model_json_schema())
# {'title': 'PromptInput', 'type': 'object', 'properties':
{'question': {'title': 'Question', 'type': 'string'}}}
print(chain_with_assign.output_schema.model_json_schema())
# {'title': 'RunnableSequenceOutput', 'type': 'object', 'properties':
{'str': {'title': 'Str',
'type': 'string'}, 'hello': {'title': 'Hello', 'type': 'string'}}}
```
### batch [¶](#langgraph.pregel.remote.RemoteGraph.batch "Permanent link")
```
batch(
    inputs: list[Input],
    config: Optional[
        Union[RunnableConfig, list[RunnableConfig]]
    ] = None,
    *,
    return_exceptions: bool = False,
    **kwargs: Optional[Any]
) -> list[Output]
```
Default implementation runs invoke in parallel using a thread pool executor.
The default implementation of batch works well for IO bound runnables.
Subclasses should override this method if they can batch more efficiently;
e.g., if the underlying Runnable uses an API which supports a batch mode.
### batch\_as\_completed [¶](#langgraph.pregel.remote.RemoteGraph.batch_as_completed "Permanent link")
```
batch_as_completed(
    inputs: Sequence[Input],
    config: Optional[
        Union[RunnableConfig, Sequence[RunnableConfig]]
    ] = None,
    *,
    return_exceptions: bool = False,
    **kwargs: Optional[Any]
) -> Iterator[tuple[int, Union[Output, Exception]]]
```
Run invoke in parallel on a list of inputs.
Yields results as they complete.
### abatch `async` [¶](#langgraph.pregel.remote.RemoteGraph.abatch "Permanent link")
```
abatch(
    inputs: list[Input],
    config: Optional[
        Union[RunnableConfig, list[RunnableConfig]]
    ] = None,
    *,
    return_exceptions: bool = False,
    **kwargs: Optional[Any]
) -> list[Output]
```
Default implementation runs ainvoke in parallel using asyncio.gather.
The default implementation of batch works well for IO bound runnables.
Subclasses should override this method if they can batch more efficiently;
e.g., if the underlying Runnable uses an API which supports a batch mode.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `inputs` | `list[Input]` | A list of inputs to the Runnable. | *required* |
| `config` | `Optional[Union[RunnableConfig, list[RunnableConfig]]]` | A config to use when invoking the Runnable. The config supports standard keys like 'tags', 'metadata' for tracing purposes, 'max\_concurrency' for controlling how much work to do in parallel, and other keys. Please refer to the RunnableConfig for more details. Defaults to None. | `None` |
| `return_exceptions` | `bool` | Whether to return exceptions instead of raising them. Defaults to False. | `False` |
| `kwargs` | `Optional[Any]` | Additional keyword arguments to pass to the Runnable. | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `list[Output]` | A list of outputs from the Runnable. |
### abatch\_as\_completed `async` [¶](#langgraph.pregel.remote.RemoteGraph.abatch_as_completed "Permanent link")
```
abatch_as_completed(
    inputs: Sequence[Input],
    config: Optional[
        Union[RunnableConfig, Sequence[RunnableConfig]]
    ] = None,
    *,
    return_exceptions: bool = False,
    **kwargs: Optional[Any]
) -> AsyncIterator[tuple[int, Union[Output, Exception]]]
```
Run ainvoke in parallel on a list of inputs.
Yields results as they complete.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `inputs` | `Sequence[Input]` | A list of inputs to the Runnable. | *required* |
| `config` | `Optional[Union[RunnableConfig, Sequence[RunnableConfig]]]` | A config to use when invoking the Runnable. The config supports standard keys like 'tags', 'metadata' for tracing purposes, 'max\_concurrency' for controlling how much work to do in parallel, and other keys. Please refer to the RunnableConfig for more details. Defaults to None. Defaults to None. | `None` |
| `return_exceptions` | `bool` | Whether to return exceptions instead of raising them. Defaults to False. | `False` |
| `kwargs` | `Optional[Any]` | Additional keyword arguments to pass to the Runnable. | `{}` |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[tuple[int, Union[Output, Exception]]]` | A tuple of the index of the input and the output from the Runnable. |
### astream\_log `async` [¶](#langgraph.pregel.remote.RemoteGraph.astream_log "Permanent link")
```
astream_log(
    input: Any,
    config: Optional[RunnableConfig] = None,
    *,
    diff: bool = True,
    with_streamed_output_list: bool = True,
    include_names: Optional[Sequence[str]] = None,
    include_types: Optional[Sequence[str]] = None,
    include_tags: Optional[Sequence[str]] = None,
    exclude_names: Optional[Sequence[str]] = None,
    exclude_types: Optional[Sequence[str]] = None,
    exclude_tags: Optional[Sequence[str]] = None,
    **kwargs: Any
) -> Union[
    AsyncIterator[RunLogPatch], AsyncIterator[RunLog]
]
```
Stream all output from a Runnable, as reported to the callback system.
This includes all inner runs of LLMs, Retrievers, Tools, etc.
Output is streamed as Log objects, which include a list of
Jsonpatch ops that describe how the state of the run has changed in each
step, and the final state of the run.
The Jsonpatch ops can be applied in order to construct state.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `Any` | The input to the Runnable. | *required* |
| `config` | `Optional[RunnableConfig]` | The config to use for the Runnable. | `None` |
| `diff` | `bool` | Whether to yield diffs between each step or the current state. | `True` |
| `with_streamed_output_list` | `bool` | Whether to yield the streamed\_output list. | `True` |
| `include_names` | `Optional[Sequence[str]]` | Only include logs with these names. | `None` |
| `include_types` | `Optional[Sequence[str]]` | Only include logs with these types. | `None` |
| `include_tags` | `Optional[Sequence[str]]` | Only include logs with these tags. | `None` |
| `exclude_names` | `Optional[Sequence[str]]` | Exclude logs with these names. | `None` |
| `exclude_types` | `Optional[Sequence[str]]` | Exclude logs with these types. | `None` |
| `exclude_tags` | `Optional[Sequence[str]]` | Exclude logs with these tags. | `None` |
| `kwargs` | `Any` | Additional keyword arguments to pass to the Runnable. | `{}` |
Yields:
| Type | Description |
| --- | --- |
| `Union[AsyncIterator[RunLogPatch], AsyncIterator[RunLog]]` | A RunLogPatch or RunLog object. |
### transform [¶](#langgraph.pregel.remote.RemoteGraph.transform "Permanent link")
```
transform(
    input: Iterator[Input],
    config: Optional[RunnableConfig] = None,
    **kwargs: Optional[Any]
) -> Iterator[Output]
```
Default implementation of transform, which buffers input and calls astream.
Subclasses should override this method if they can start producing output while
input is still being generated.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `Iterator[Input]` | An iterator of inputs to the Runnable. | *required* |
| `config` | `Optional[RunnableConfig]` | The config to use for the Runnable. Defaults to None. | `None` |
| `kwargs` | `Optional[Any]` | Additional keyword arguments to pass to the Runnable. | `{}` |
Yields:
| Type | Description |
| --- | --- |
| `Output` | The output of the Runnable. |
### atransform `async` [¶](#langgraph.pregel.remote.RemoteGraph.atransform "Permanent link")
```
atransform(
    input: AsyncIterator[Input],
    config: Optional[RunnableConfig] = None,
    **kwargs: Optional[Any]
) -> AsyncIterator[Output]
```
Default implementation of atransform, which buffers input and calls astream.
Subclasses should override this method if they can start producing output while
input is still being generated.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `AsyncIterator[Input]` | An async iterator of inputs to the Runnable. | *required* |
| `config` | `Optional[RunnableConfig]` | The config to use for the Runnable. Defaults to None. | `None` |
| `kwargs` | `Optional[Any]` | Additional keyword arguments to pass to the Runnable. | `{}` |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[Output]` | The output of the Runnable. |
### bind [¶](#langgraph.pregel.remote.RemoteGraph.bind "Permanent link")
```
bind(**kwargs: Any) -> Runnable[Input, Output]
```
Bind arguments to a Runnable, returning a new Runnable.
Useful when a Runnable in a chain requires an argument that is not
in the output of the previous Runnable or included in the user input.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `kwargs` | `Any` | The arguments to bind to the Runnable. | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `Runnable[Input, Output]` | A new Runnable with the arguments bound. |
Example:
.. code-block:: python
```
from langchain_ollama import ChatOllama
from langchain_core.output_parsers import StrOutputParser
llm = ChatOllama(model='llama2')
# Without bind.
chain = (
    llm
    | StrOutputParser()
)
chain.invoke("Repeat quoted words exactly: 'One two three four five.'")
# Output is 'One two three four five.'
# With bind.
chain = (
    llm.bind(stop=["three"])
    | StrOutputParser()
)
chain.invoke("Repeat quoted words exactly: 'One two three four five.'")
# Output is 'One two'
```
### with\_listeners [¶](#langgraph.pregel.remote.RemoteGraph.with_listeners "Permanent link")
```
with_listeners(
    *,
    on_start: Optional[
        Union[
            Callable[[Run], None],
            Callable[[Run, RunnableConfig], None],
        ]
    ] = None,
    on_end: Optional[
        Union[
            Callable[[Run], None],
            Callable[[Run, RunnableConfig], None],
        ]
    ] = None,
    on_error: Optional[
        Union[
            Callable[[Run], None],
            Callable[[Run, RunnableConfig], None],
        ]
    ] = None
) -> Runnable[Input, Output]
```
Bind lifecycle listeners to a Runnable, returning a new Runnable.
on\_start: Called before the Runnable starts running, with the Run object.
on\_end: Called after the Runnable finishes running, with the Run object.
on\_error: Called if the Runnable throws an error, with the Run object.
The Run object contains information about the run, including its id,
type, input, output, error, start\_time, end\_time, and any tags or metadata
added to the run.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `on_start` | `Optional[Union[Callable[[Run], None], Callable[[Run, RunnableConfig], None]]]` | Called before the Runnable starts running. Defaults to None. | `None` |
| `on_end` | `Optional[Union[Callable[[Run], None], Callable[[Run, RunnableConfig], None]]]` | Called after the Runnable finishes running. Defaults to None. | `None` |
| `on_error` | `Optional[Union[Callable[[Run], None], Callable[[Run, RunnableConfig], None]]]` | Called if the Runnable throws an error. Defaults to None. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Runnable[Input, Output]` | A new Runnable with the listeners bound. |
Example:
.. code-block:: python
```
from langchain_core.runnables import RunnableLambda
from langchain_core.tracers.schemas import Run
import time
def test_runnable(time_to_sleep : int):
    time.sleep(time_to_sleep)
def fn_start(run_obj: Run):
    print("start_time:", run_obj.start_time)
def fn_end(run_obj: Run):
    print("end_time:", run_obj.end_time)
chain = RunnableLambda(test_runnable).with_listeners(
    on_start=fn_start,
    on_end=fn_end
)
chain.invoke(2)
```
### with\_alisteners [¶](#langgraph.pregel.remote.RemoteGraph.with_alisteners "Permanent link")
```
with_alisteners(
    *,
    on_start: Optional[AsyncListener] = None,
    on_end: Optional[AsyncListener] = None,
    on_error: Optional[AsyncListener] = None
) -> Runnable[Input, Output]
```
Bind async lifecycle listeners to a Runnable, returning a new Runnable.
on\_start: Asynchronously called before the Runnable starts running.
on\_end: Asynchronously called after the Runnable finishes running.
on\_error: Asynchronously called if the Runnable throws an error.
The Run object contains information about the run, including its id,
type, input, output, error, start\_time, end\_time, and any tags or metadata
added to the run.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `on_start` | `Optional[AsyncListener]` | Asynchronously called before the Runnable starts running. Defaults to None. | `None` |
| `on_end` | `Optional[AsyncListener]` | Asynchronously called after the Runnable finishes running. Defaults to None. | `None` |
| `on_error` | `Optional[AsyncListener]` | Asynchronously called if the Runnable throws an error. Defaults to None. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Runnable[Input, Output]` | A new Runnable with the listeners bound. |
Example:
.. code-block:: python
```
from langchain_core.runnables import RunnableLambda, Runnable
from datetime import datetime, timezone
import time
import asyncio
def format_t(timestamp: float) -> str:
    return datetime.fromtimestamp(timestamp, tz=timezone.utc).isoformat()
async def test_runnable(time_to_sleep : int):
    print(f"Runnable[{time_to_sleep}s]: starts at {format_t(time.time())}")
    await asyncio.sleep(time_to_sleep)
    print(f"Runnable[{time_to_sleep}s]: ends at {format_t(time.time())}")
async def fn_start(run_obj : Runnable):
    print(f"on start callback starts at {format_t(time.time())}")
    await asyncio.sleep(3)
    print(f"on start callback ends at {format_t(time.time())}")
async def fn_end(run_obj : Runnable):
    print(f"on end callback starts at {format_t(time.time())}")
    await asyncio.sleep(2)
    print(f"on end callback ends at {format_t(time.time())}")
runnable = RunnableLambda(test_runnable).with_alisteners(
    on_start=fn_start,
    on_end=fn_end
)
async def concurrent_runs():
    await asyncio.gather(runnable.ainvoke(2), runnable.ainvoke(3))
asyncio.run(concurrent_runs())
Result:
on start callback starts at 2025-03-01T07:05:22.875378+00:00
on start callback starts at 2025-03-01T07:05:22.875495+00:00
on start callback ends at 2025-03-01T07:05:25.878862+00:00
on start callback ends at 2025-03-01T07:05:25.878947+00:00
Runnable[2s]: starts at 2025-03-01T07:05:25.879392+00:00
Runnable[3s]: starts at 2025-03-01T07:05:25.879804+00:00
Runnable[2s]: ends at 2025-03-01T07:05:27.881998+00:00
on end callback starts at 2025-03-01T07:05:27.882360+00:00
Runnable[3s]: ends at 2025-03-01T07:05:28.881737+00:00
on end callback starts at 2025-03-01T07:05:28.882428+00:00
on end callback ends at 2025-03-01T07:05:29.883893+00:00
on end callback ends at 2025-03-01T07:05:30.884831+00:00
```
### with\_types [¶](#langgraph.pregel.remote.RemoteGraph.with_types "Permanent link")
```
with_types(
    *,
    input_type: Optional[type[Input]] = None,
    output_type: Optional[type[Output]] = None
) -> Runnable[Input, Output]
```
Bind input and output types to a Runnable, returning a new Runnable.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input_type` | `Optional[type[Input]]` | The input type to bind to the Runnable. Defaults to None. | `None` |
| `output_type` | `Optional[type[Output]]` | The output type to bind to the Runnable. Defaults to None. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Runnable[Input, Output]` | A new Runnable with the types bound. |
### with\_retry [¶](#langgraph.pregel.remote.RemoteGraph.with_retry "Permanent link")
```
with_retry(
    *,
    retry_if_exception_type: tuple[
        type[BaseException], ...
    ] = (Exception,),
    wait_exponential_jitter: bool = True,
    exponential_jitter_params: Optional[
        ExponentialJitterParams
    ] = None,
    stop_after_attempt: int = 3
) -> Runnable[Input, Output]
```
Create a new Runnable that retries the original Runnable on exceptions.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `retry_if_exception_type` | `tuple[type[BaseException], ...]` | A tuple of exception types to retry on. Defaults to (Exception,). | `(Exception,)` |
| `wait_exponential_jitter` | `bool` | Whether to add jitter to the wait time between retries. Defaults to True. | `True` |
| `stop_after_attempt` | `int` | The maximum number of attempts to make before giving up. Defaults to 3. | `3` |
| `exponential_jitter_params` | `Optional[ExponentialJitterParams]` | Parameters for `tenacity.wait_exponential_jitter`. Namely: `initial`, `max`, `exp_base`, and `jitter` (all float values). | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Runnable[Input, Output]` | A new Runnable that retries the original Runnable on exceptions. |
Example:
.. code-block:: python
```
from langchain_core.runnables import RunnableLambda
count = 0
def _lambda(x: int) -> None:
    global count
    count = count + 1
    if x == 1:
        raise ValueError("x is 1")
    else:
         pass
runnable = RunnableLambda(_lambda)
try:
    runnable.with_retry(
        stop_after_attempt=2,
        retry_if_exception_type=(ValueError,),
    ).invoke(1)
except ValueError:
    pass
assert (count == 2)
```
### map [¶](#langgraph.pregel.remote.RemoteGraph.map "Permanent link")
```
map() -> Runnable[list[Input], list[Output]]
```
Return a new Runnable that maps a list of inputs to a list of outputs.
Calls invoke() with each input.
Returns:
| Type | Description |
| --- | --- |
| `Runnable[list[Input], list[Output]]` | A new Runnable that maps a list of inputs to a list of outputs. |
Example:
```
.. code-block:: python
        from langchain_core.runnables import RunnableLambda
        def _lambda(x: int) -> int:
            return x + 1
        runnable = RunnableLambda(_lambda)
        print(runnable.map().invoke([1, 2, 3])) # [2, 3, 4]
```
### with\_fallbacks [¶](#langgraph.pregel.remote.RemoteGraph.with_fallbacks "Permanent link")
```
with_fallbacks(
    fallbacks: Sequence[Runnable[Input, Output]],
    *,
    exceptions_to_handle: tuple[
        type[BaseException], ...
    ] = (Exception,),
    exception_key: Optional[str] = None
) -> RunnableWithFallbacks[Input, Output]
```
Add fallbacks to a Runnable, returning a new Runnable.
The new Runnable will try the original Runnable, and then each fallback
in order, upon failures.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `fallbacks` | `Sequence[Runnable[Input, Output]]` | A sequence of runnables to try if the original Runnable fails. | *required* |
| `exceptions_to_handle` | `tuple[type[BaseException], ...]` | A tuple of exception types to handle. Defaults to (Exception,). | `(Exception,)` |
| `exception_key` | `Optional[str]` | If string is specified then handled exceptions will be passed to fallbacks as part of the input under the specified key. If None, exceptions will not be passed to fallbacks. If used, the base Runnable and its fallbacks must accept a dictionary as input. Defaults to None. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `RunnableWithFallbacks[Input, Output]` | A new Runnable that will try the original Runnable, and then each |
| `RunnableWithFallbacks[Input, Output]` | fallback in order, upon failures. |
Example:
```
.. code-block:: python
    from typing import Iterator
    from langchain_core.runnables import RunnableGenerator
    def _generate_immediate_error(input: Iterator) -> Iterator[str]:
        raise ValueError()
        yield ""
    def _generate(input: Iterator) -> Iterator[str]:
        yield from "foo bar"
    runnable = RunnableGenerator(_generate_immediate_error).with_fallbacks(
        [RunnableGenerator(_generate)]
        )
    print(''.join(runnable.stream({}))) #foo bar
```
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `fallbacks` | `Sequence[Runnable[Input, Output]]` | A sequence of runnables to try if the original Runnable fails. | *required* |
| `exceptions_to_handle` | `tuple[type[BaseException], ...]` | A tuple of exception types to handle. | `(Exception,)` |
| `exception_key` | `Optional[str]` | If string is specified then handled exceptions will be passed to fallbacks as part of the input under the specified key. If None, exceptions will not be passed to fallbacks. If used, the base Runnable and its fallbacks must accept a dictionary as input. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `RunnableWithFallbacks[Input, Output]` | A new Runnable that will try the original Runnable, and then each |
| `RunnableWithFallbacks[Input, Output]` | fallback in order, upon failures. |
### as\_tool [¶](#langgraph.pregel.remote.RemoteGraph.as_tool "Permanent link")
```
as_tool(
    args_schema: Optional[type[BaseModel]] = None,
    *,
    name: Optional[str] = None,
    description: Optional[str] = None,
    arg_types: Optional[dict[str, type]] = None
) -> BaseTool
```
Create a BaseTool from a Runnable.
`as_tool` will instantiate a BaseTool with a name, description, and
`args_schema` from a Runnable. Where possible, schemas are inferred
from `runnable.get_input_schema`. Alternatively (e.g., if the
Runnable takes a dict as input and the specific dict keys are not typed),
the schema can be specified directly with `args_schema`. You can also
pass `arg_types` to just specify the required arguments and their types.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `args_schema` | `Optional[type[BaseModel]]` | The schema for the tool. Defaults to None. | `None` |
| `name` | `Optional[str]` | The name of the tool. Defaults to None. | `None` |
| `description` | `Optional[str]` | The description of the tool. Defaults to None. | `None` |
| `arg_types` | `Optional[dict[str, type]]` | A dictionary of argument names to types. Defaults to None. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `BaseTool` | A BaseTool instance. |
Typed dict input:
.. code-block:: python
```
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableLambda
class Args(TypedDict):
    a: int
    b: list[int]
def f(x: Args) -> str:
    return str(x["a"] * max(x["b"]))
runnable = RunnableLambda(f)
as_tool = runnable.as_tool()
as_tool.invoke({"a": 3, "b": [1, 2]})
```
`dict` input, specifying schema via `args_schema`:
.. code-block:: python
```
from typing import Any
from pydantic import BaseModel, Field
from langchain_core.runnables import RunnableLambda
def f(x: dict[str, Any]) -> str:
    return str(x["a"] * max(x["b"]))
class FSchema(BaseModel):
    """Apply a function to an integer and list of integers."""
    a: int = Field(..., description="Integer")
    b: list[int] = Field(..., description="List of ints")
runnable = RunnableLambda(f)
as_tool = runnable.as_tool(FSchema)
as_tool.invoke({"a": 3, "b": [1, 2]})
```
`dict` input, specifying schema via `arg_types`:
.. code-block:: python
```
from typing import Any
from langchain_core.runnables import RunnableLambda
def f(x: dict[str, Any]) -> str:
    return str(x["a"] * max(x["b"]))
runnable = RunnableLambda(f)
as_tool = runnable.as_tool(arg_types={"a": int, "b": list[int]})
as_tool.invoke({"a": 3, "b": [1, 2]})
```
String input:
.. code-block:: python
```
from langchain_core.runnables import RunnableLambda
def f(x: str) -> str:
    return x + "a"
def g(x: str) -> str:
    return x + "z"
runnable = RunnableLambda(f) | g
as_tool = runnable.as_tool()
as_tool.invoke("b")
```
.. versionadded:: 0.2.14
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/remote_graph/)
