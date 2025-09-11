# Graphs

# Graph Definitions[¶](#graph-definitions "Permanent link")
## StateGraph [¶](#langgraph.graph.state.StateGraph "Permanent link")
Bases: `Generic[StateT, ContextT, InputT, OutputT]`
A graph whose nodes communicate by reading and writing to a shared state.
The signature of each node is State -> Partial.
Each state key can optionally be annotated with a reducer function that
will be used to aggregate the values of that key received from multiple nodes.
The signature of a reducer function is (Value, Value) -> Value.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `state_schema` | `type[StateT]` | The schema class that defines the state. | *required* |
| `context_schema` | `type[ContextT] | None` | The schema class that defines the runtime context. Use this to expose immutable context data to your nodes, like user\_id, db\_conn, etc. | `None` |
| `input_schema` | `type[InputT] | None` | The schema class that defines the input to the graph. | `None` |
| `output_schema` | `type[OutputT] | None` | The schema class that defines the output from the graph. | `None` |
`config_schema` Deprecated
The `config_schema` parameter is deprecated in v0.6.0 and support will be removed in v2.0.0.
Please use `context_schema` instead to specify the schema for run-scoped context.
Example
```
from langchain_core.runnables import RunnableConfig
from typing_extensions import Annotated, TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import StateGraph
from langgraph.runtime import Runtime
def reducer(a: list, b: int | None) -> list:
    if b is not None:
        return a + [b]
    return a
class State(TypedDict):
    x: Annotated[list, reducer]
class Context(TypedDict):
    r: float
graph = StateGraph(state_schema=State, context_schema=Context)
def node(state: State, runtime: Runtime[Context]) -> dict:
    r = runtime.context.get("r", 1.0)
    x = state["x"][-1]
    next_value = x * r * (1 - x)
    return {"x": next_value}
graph.add_node("A", node)
graph.set_entry_point("A")
graph.set_finish_point("A")
compiled = graph.compile()
step1 = compiled.invoke({"x": 0.5}, context={"r": 3.0})
# {'x': [0.5, 0.75]}
```
Methods:
| Name | Description |
| --- | --- |
| `add_node` | Add a new node to the state graph. |
| `add_edge` | Add a directed edge from the start node (or list of start nodes) to the end node. |
| `add_conditional_edges` | Add a conditional edge from the starting node to any number of destination nodes. |
| `add_sequence` | Add a sequence of nodes that will be executed in the provided order. |
| `compile` | Compiles the state graph into a `CompiledStateGraph` object. |
### add\_node [¶](#langgraph.graph.state.StateGraph.add_node "Permanent link")
```
add_node(
    node: str | StateNode[NodeInputT, ContextT],
    action: StateNode[NodeInputT, ContextT] | None = None,
    *,
    defer: bool = False,
    metadata: dict[str, Any] | None = None,
    input_schema: type[NodeInputT] | None = None,
    retry_policy: (
        RetryPolicy | Sequence[RetryPolicy] | None
    ) = None,
    cache_policy: CachePolicy | None = None,
    destinations: (
        dict[str, str] | tuple[str, ...] | None
    ) = None,
    **kwargs: Unpack[DeprecatedKwargs]
) -> Self
```
Add a new node to the state graph.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `node` | `str | StateNode[NodeInputT, ContextT]` | The function or runnable this node will run. If a string is provided, it will be used as the node name, and action will be used as the function or runnable. | *required* |
| `action` | `StateNode[NodeInputT, ContextT] | None` | The action associated with the node. (default: None) Will be used as the node function or runnable if `node` is a string (node name). | `None` |
| `defer` | `bool` | Whether to defer the execution of the node until the run is about to end. | `False` |
| `metadata` | `dict[str, Any] | None` | The metadata associated with the node. (default: None) | `None` |
| `input_schema` | `type[NodeInputT] | None` | The input schema for the node. (default: the graph's state schema) | `None` |
| `retry_policy` | `RetryPolicy | Sequence[RetryPolicy] | None` | The retry policy for the node. (default: None) If a sequence is provided, the first matching policy will be applied. | `None` |
| `cache_policy` | `CachePolicy | None` | The cache policy for the node. (default: None) | `None` |
| `destinations` | `dict[str, str] | tuple[str, ...] | None` | Destinations that indicate where a node can route to. This is useful for edgeless graphs with nodes that return `Command` objects. If a dict is provided, the keys will be used as the target node names and the values will be used as the labels for the edges. If a tuple is provided, the values will be used as the target node names. NOTE: this is only used for graph rendering and doesn't have any effect on the graph execution. | `None` |
Example
```
from typing_extensions import TypedDict
from langchain_core.runnables import RunnableConfig
from langgraph.graph import START, StateGraph
class State(TypedDict):
    x: int
def my_node(state: State, config: RunnableConfig) -> State:
    return {"x": state["x"] + 1}
builder = StateGraph(State)
builder.add_node(my_node)  # node name will be 'my_node'
builder.add_edge(START, "my_node")
graph = builder.compile()
graph.invoke({"x": 1})
# {'x': 2}
```
Customize the name:
```
builder = StateGraph(State)
builder.add_node("my_fair_node", my_node)
builder.add_edge(START, "my_fair_node")
graph = builder.compile()
graph.invoke({"x": 1})
# {'x': 2}
```
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `Self` | `Self` | The instance of the state graph, allowing for method chaining. |
### add\_edge [¶](#langgraph.graph.state.StateGraph.add_edge "Permanent link")
```
add_edge(start_key: str | list[str], end_key: str) -> Self
```
Add a directed edge from the start node (or list of start nodes) to the end node.
When a single start node is provided, the graph will wait for that node to complete
before executing the end node. When multiple start nodes are provided,
the graph will wait for ALL of the start nodes to complete before executing the end node.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `start_key` | `str | list[str]` | The key(s) of the start node(s) of the edge. | *required* |
| `end_key` | `str` | The key of the end node of the edge. | *required* |
Raises:
| Type | Description |
| --- | --- |
| `ValueError` | If the start key is 'END' or if the start key or end key is not present in the graph. |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `Self` | `Self` | The instance of the state graph, allowing for method chaining. |
### add\_conditional\_edges [¶](#langgraph.graph.state.StateGraph.add_conditional_edges "Permanent link")
```
add_conditional_edges(
    source: str,
    path: (
        Callable[..., Hashable | Sequence[Hashable]]
        | Callable[
            ..., Awaitable[Hashable | Sequence[Hashable]]
        ]
        | Runnable[Any, Hashable | Sequence[Hashable]]
    ),
    path_map: dict[Hashable, str] | list[str] | None = None,
) -> Self
```
Add a conditional edge from the starting node to any number of destination nodes.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `source` | `str` | The starting node. This conditional edge will run when exiting this node. | *required* |
| `path` | `Callable[..., Hashable | Sequence[Hashable]] | Callable[..., Awaitable[Hashable | Sequence[Hashable]]] | Runnable[Any, Hashable | Sequence[Hashable]]` | The callable that determines the next node or nodes. If not specifying `path_map` it should return one or more nodes. If it returns END, the graph will stop execution. | *required* |
| `path_map` | `dict[Hashable, str] | list[str] | None` | Optional mapping of paths to node names. If omitted the paths returned by `path` should be node names. | `None` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `Self` | `Self` | The instance of the graph, allowing for method chaining. |
Without typehints on the `path` function's return value (e.g., `-> Literal["foo", "__end__"]:`)
or a path\_map, the graph visualization assumes the edge could transition to any node in the graph.
### add\_sequence [¶](#langgraph.graph.state.StateGraph.add_sequence "Permanent link")
```
add_sequence(
    nodes: Sequence[
        StateNode[NodeInputT, ContextT]
        | tuple[str, StateNode[NodeInputT, ContextT]]
    ],
) -> Self
```
Add a sequence of nodes that will be executed in the provided order.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `nodes` | `Sequence[StateNode[NodeInputT, ContextT] | tuple[str, StateNode[NodeInputT, ContextT]]]` | A sequence of StateNodes (callables that accept a state arg) or (name, StateNode) tuples. If no names are provided, the name will be inferred from the node object (e.g. a runnable or a callable name). Each node will be executed in the order provided. | *required* |
Raises:
| Type | Description |
| --- | --- |
| `ValueError` | if the sequence is empty. |
| `ValueError` | if the sequence contains duplicate node names. |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `Self` | `Self` | The instance of the state graph, allowing for method chaining. |
### compile [¶](#langgraph.graph.state.StateGraph.compile "Permanent link")
```
compile(
    checkpointer: Checkpointer = None,
    *,
    cache: BaseCache | None = None,
    store: BaseStore | None = None,
    interrupt_before: All | list[str] | None = None,
    interrupt_after: All | list[str] | None = None,
    debug: bool = False,
    name: str | None = None
) -> CompiledStateGraph[StateT, ContextT, InputT, OutputT]
```
Compiles the state graph into a `CompiledStateGraph` object.
The compiled graph implements the `Runnable` interface and can be invoked,
streamed, batched, and run asynchronously.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `checkpointer` | `Checkpointer` | A checkpoint saver object or flag. If provided, this Checkpointer serves as a fully versioned "short-term memory" for the graph, allowing it to be paused, resumed, and replayed from any point. If None, it may inherit the parent graph's checkpointer when used as a subgraph. If False, it will not use or inherit any checkpointer. | `None` |
| `interrupt_before` | `All | list[str] | None` | An optional list of node names to interrupt before. | `None` |
| `interrupt_after` | `All | list[str] | None` | An optional list of node names to interrupt after. | `None` |
| `debug` | `bool` | A flag indicating whether to enable debug mode. | `False` |
| `name` | `str | None` | The name to use for the compiled graph. | `None` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `CompiledStateGraph` | `CompiledStateGraph[StateT, ContextT, InputT, OutputT]` | The compiled state graph. |
## CompiledStateGraph [¶](#langgraph.graph.state.CompiledStateGraph "Permanent link")
Bases: `Pregel[StateT, ContextT, InputT, OutputT]`, `Generic[StateT, ContextT, InputT, OutputT]`
Methods:
| Name | Description |
| --- | --- |
| `stream` | Stream graph steps for a single input. |
| `astream` | Asynchronously stream graph steps for a single input. |
| `invoke` | Run the graph with a single input and config. |
| `ainvoke` | Asynchronously invoke the graph on a single input. |
| `get_state` | Get the current state of the graph. |
| `aget_state` | Get the current state of the graph. |
| `get_state_history` | Get the history of the state of the graph. |
| `aget_state_history` | Asynchronously get the history of the state of the graph. |
| `update_state` | Update the state of the graph with the given values, as if they came from |
| `aupdate_state` | Asynchronously update the state of the graph with the given values, as if they came from |
| `bulk_update_state` | Apply updates to the graph state in bulk. Requires a checkpointer to be set. |
| `abulk_update_state` | Asynchronously apply updates to the graph state in bulk. Requires a checkpointer to be set. |
| `get_graph` | Return a drawable representation of the computation graph. |
| `aget_graph` | Return a drawable representation of the computation graph. |
| `get_subgraphs` | Get the subgraphs of the graph. |
| `aget_subgraphs` | Get the subgraphs of the graph. |
| `with_config` | Create a copy of the Pregel object with an updated config. |
### stream [¶](#langgraph.graph.state.CompiledStateGraph.stream "Permanent link")
```
stream(
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: (
        StreamMode | Sequence[StreamMode] | None
    ) = None,
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool = False,
    debug: bool | None = None,
    **kwargs: Unpack[DeprecatedKwargs]
) -> Iterator[dict[str, Any] | Any]
```
Stream graph steps for a single input.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `InputT | Command | None` | The input to the graph. | *required* |
| `config` | `RunnableConfig | None` | The configuration to use for the run. | `None` |
| `context` | `ContextT | None` | The static context to use for the run.  Added in version 0.6.0. | `None` |
| `stream_mode` | `StreamMode | Sequence[StreamMode] | None` | The mode to stream output, defaults to `self.stream_mode`. Options are:   * `"values"`: Emit all values in the state after each step, including interrupts.   When used with functional API, values are emitted once at the end of the workflow. * `"updates"`: Emit only the node or task names and updates returned by the nodes or tasks after each step.   If multiple updates are made in the same step (e.g. multiple nodes are run) then those updates are emitted separately. * `"custom"`: Emit custom data from inside nodes or tasks using `StreamWriter`. * `"messages"`: Emit LLM messages token-by-token together with metadata for any LLM invocations inside nodes or tasks.   Will be emitted as 2-tuples `(LLM token, metadata)`. * `"checkpoints"`: Emit an event when a checkpoint is created, in the same format as returned by get\_state(). * `"tasks"`: Emit events when tasks start and finish, including their results and errors.   You can pass a list as the `stream_mode` parameter to stream multiple modes at once. The streamed outputs will be tuples of `(mode, data)`.  See [LangGraph streaming guide](https://langchain-ai.github.io/langgraph/how-tos/streaming/) for more details. | `None` |
| `print_mode` | `StreamMode | Sequence[StreamMode]` | Accepts the same values as `stream_mode`, but only prints the output to the console, for debugging purposes. Does not affect the output of the graph in any way. | `()` |
| `output_keys` | `str | Sequence[str] | None` | The keys to stream, defaults to all non-context channels. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Nodes to interrupt before, defaults to all nodes in the graph. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Nodes to interrupt after, defaults to all nodes in the graph. | `None` |
| `durability` | `Durability | None` | The durability mode for the graph execution, defaults to "async". Options are: - `"sync"`: Changes are persisted synchronously before the next step starts. - `"async"`: Changes are persisted asynchronously while the next step executes. - `"exit"`: Changes are persisted only when the graph exits. | `None` |
| `subgraphs` | `bool` | Whether to stream events from inside subgraphs, defaults to False. If True, the events will be emitted as tuples `(namespace, data)`, or `(namespace, mode, data)` if `stream_mode` is a list, where `namespace` is a tuple with the path to the node where a subgraph is invoked, e.g. `("parent_node:<task_id>", "child_node:<task_id>")`.  See [LangGraph streaming guide](https://langchain-ai.github.io/langgraph/how-tos/streaming/) for more details. | `False` |
Yields:
| Type | Description |
| --- | --- |
| `dict[str, Any] | Any` | The output of each step in the graph. The output shape depends on the stream\_mode. |
### astream `async` [¶](#langgraph.graph.state.CompiledStateGraph.astream "Permanent link")
```
astream(
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: (
        StreamMode | Sequence[StreamMode] | None
    ) = None,
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    subgraphs: bool = False,
    debug: bool | None = None,
    **kwargs: Unpack[DeprecatedKwargs]
) -> AsyncIterator[dict[str, Any] | Any]
```
Asynchronously stream graph steps for a single input.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `InputT | Command | None` | The input to the graph. | *required* |
| `config` | `RunnableConfig | None` | The configuration to use for the run. | `None` |
| `context` | `ContextT | None` | The static context to use for the run.  Added in version 0.6.0. | `None` |
| `stream_mode` | `StreamMode | Sequence[StreamMode] | None` | The mode to stream output, defaults to `self.stream_mode`. Options are:   * `"values"`: Emit all values in the state after each step, including interrupts.   When used with functional API, values are emitted once at the end of the workflow. * `"updates"`: Emit only the node or task names and updates returned by the nodes or tasks after each step.   If multiple updates are made in the same step (e.g. multiple nodes are run) then those updates are emitted separately. * `"custom"`: Emit custom data from inside nodes or tasks using `StreamWriter`. * `"messages"`: Emit LLM messages token-by-token together with metadata for any LLM invocations inside nodes or tasks.   Will be emitted as 2-tuples `(LLM token, metadata)`. * `"debug"`: Emit debug events with as much information as possible for each step.   You can pass a list as the `stream_mode` parameter to stream multiple modes at once. The streamed outputs will be tuples of `(mode, data)`.  See [LangGraph streaming guide](https://langchain-ai.github.io/langgraph/how-tos/streaming/) for more details. | `None` |
| `print_mode` | `StreamMode | Sequence[StreamMode]` | Accepts the same values as `stream_mode`, but only prints the output to the console, for debugging purposes. Does not affect the output of the graph in any way. | `()` |
| `output_keys` | `str | Sequence[str] | None` | The keys to stream, defaults to all non-context channels. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Nodes to interrupt before, defaults to all nodes in the graph. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Nodes to interrupt after, defaults to all nodes in the graph. | `None` |
| `durability` | `Durability | None` | The durability mode for the graph execution, defaults to "async". Options are: - `"sync"`: Changes are persisted synchronously before the next step starts. - `"async"`: Changes are persisted asynchronously while the next step executes. - `"exit"`: Changes are persisted only when the graph exits. | `None` |
| `subgraphs` | `bool` | Whether to stream events from inside subgraphs, defaults to False. If True, the events will be emitted as tuples `(namespace, data)`, or `(namespace, mode, data)` if `stream_mode` is a list, where `namespace` is a tuple with the path to the node where a subgraph is invoked, e.g. `("parent_node:<task_id>", "child_node:<task_id>")`.  See [LangGraph streaming guide](https://langchain-ai.github.io/langgraph/how-tos/streaming/) for more details. | `False` |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[dict[str, Any] | Any]` | The output of each step in the graph. The output shape depends on the stream\_mode. |
### invoke [¶](#langgraph.graph.state.CompiledStateGraph.invoke "Permanent link")
```
invoke(
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode = "values",
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    **kwargs: Any
) -> dict[str, Any] | Any
```
Run the graph with a single input and config.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `InputT | Command | None` | The input data for the graph. It can be a dictionary or any other type. | *required* |
| `config` | `RunnableConfig | None` | Optional. The configuration for the graph run. | `None` |
| `context` | `ContextT | None` | The static context to use for the run.  Added in version 0.6.0. | `None` |
| `stream_mode` | `StreamMode` | Optional[str]. The stream mode for the graph run. Default is "values". | `'values'` |
| `print_mode` | `StreamMode | Sequence[StreamMode]` | Accepts the same values as `stream_mode`, but only prints the output to the console, for debugging purposes. Does not affect the output of the graph in any way. | `()` |
| `output_keys` | `str | Sequence[str] | None` | Optional. The output keys to retrieve from the graph run. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Optional. The nodes to interrupt the graph run before. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Optional. The nodes to interrupt the graph run after. | `None` |
| `durability` | `Durability | None` | The durability mode for the graph execution, defaults to "async". Options are: - `"sync"`: Changes are persisted synchronously before the next step starts. - `"async"`: Changes are persisted asynchronously while the next step executes. - `"exit"`: Changes are persisted only when the graph exits. | `None` |
| `**kwargs` | `Any` | Additional keyword arguments to pass to the graph run. | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any] | Any` | The output of the graph run. If stream\_mode is "values", it returns the latest output. |
| `dict[str, Any] | Any` | If stream\_mode is not "values", it returns a list of output chunks. |
### ainvoke `async` [¶](#langgraph.graph.state.CompiledStateGraph.ainvoke "Permanent link")
```
ainvoke(
    input: InputT | Command | None,
    config: RunnableConfig | None = None,
    *,
    context: ContextT | None = None,
    stream_mode: StreamMode = "values",
    print_mode: StreamMode | Sequence[StreamMode] = (),
    output_keys: str | Sequence[str] | None = None,
    interrupt_before: All | Sequence[str] | None = None,
    interrupt_after: All | Sequence[str] | None = None,
    durability: Durability | None = None,
    **kwargs: Any
) -> dict[str, Any] | Any
```
Asynchronously invoke the graph on a single input.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `input` | `InputT | Command | None` | The input data for the computation. It can be a dictionary or any other type. | *required* |
| `config` | `RunnableConfig | None` | Optional. The configuration for the computation. | `None` |
| `context` | `ContextT | None` | The static context to use for the run.  Added in version 0.6.0. | `None` |
| `stream_mode` | `StreamMode` | Optional. The stream mode for the computation. Default is "values". | `'values'` |
| `print_mode` | `StreamMode | Sequence[StreamMode]` | Accepts the same values as `stream_mode`, but only prints the output to the console, for debugging purposes. Does not affect the output of the graph in any way. | `()` |
| `output_keys` | `str | Sequence[str] | None` | Optional. The output keys to include in the result. Default is None. | `None` |
| `interrupt_before` | `All | Sequence[str] | None` | Optional. The nodes to interrupt before. Default is None. | `None` |
| `interrupt_after` | `All | Sequence[str] | None` | Optional. The nodes to interrupt after. Default is None. | `None` |
| `durability` | `Durability | None` | The durability mode for the graph execution, defaults to "async". Options are: - `"sync"`: Changes are persisted synchronously before the next step starts. - `"async"`: Changes are persisted asynchronously while the next step executes. - `"exit"`: Changes are persisted only when the graph exits. | `None` |
| `**kwargs` | `Any` | Additional keyword arguments. | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `dict[str, Any] | Any` | The result of the computation. If stream\_mode is "values", it returns the latest value. |
| `dict[str, Any] | Any` | If stream\_mode is "chunks", it returns a list of chunks. |
### get\_state [¶](#langgraph.graph.state.CompiledStateGraph.get_state "Permanent link")
```
get_state(
    config: RunnableConfig, *, subgraphs: bool = False
) -> StateSnapshot
```
Get the current state of the graph.
### aget\_state `async` [¶](#langgraph.graph.state.CompiledStateGraph.aget_state "Permanent link")
```
aget_state(
    config: RunnableConfig, *, subgraphs: bool = False
) -> StateSnapshot
```
Get the current state of the graph.
### get\_state\_history [¶](#langgraph.graph.state.CompiledStateGraph.get_state_history "Permanent link")
```
get_state_history(
    config: RunnableConfig,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[StateSnapshot]
```
Get the history of the state of the graph.
### aget\_state\_history `async` [¶](#langgraph.graph.state.CompiledStateGraph.aget_state_history "Permanent link")
```
aget_state_history(
    config: RunnableConfig,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[StateSnapshot]
```
Asynchronously get the history of the state of the graph.
### update\_state [¶](#langgraph.graph.state.CompiledStateGraph.update_state "Permanent link")
```
update_state(
    config: RunnableConfig,
    values: dict[str, Any] | Any | None,
    as_node: str | None = None,
    task_id: str | None = None,
) -> RunnableConfig
```
Update the state of the graph with the given values, as if they came from
node `as_node`. If `as_node` is not provided, it will be set to the last node
that updated the state, if not ambiguous.
### aupdate\_state `async` [¶](#langgraph.graph.state.CompiledStateGraph.aupdate_state "Permanent link")
```
aupdate_state(
    config: RunnableConfig,
    values: dict[str, Any] | Any,
    as_node: str | None = None,
    task_id: str | None = None,
) -> RunnableConfig
```
Asynchronously update the state of the graph with the given values, as if they came from
node `as_node`. If `as_node` is not provided, it will be set to the last node
that updated the state, if not ambiguous.
### bulk\_update\_state [¶](#langgraph.graph.state.CompiledStateGraph.bulk_update_state "Permanent link")
```
bulk_update_state(
    config: RunnableConfig,
    supersteps: Sequence[Sequence[StateUpdate]],
) -> RunnableConfig
```
Apply updates to the graph state in bulk. Requires a checkpointer to be set.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to apply the updates to. | *required* |
| `supersteps` | `Sequence[Sequence[StateUpdate]]` | A list of supersteps, each including a list of updates to apply sequentially to a graph state. Each update is a tuple of the form `(values, as_node, task_id)` where task\_id is optional. | *required* |
Raises:
| Type | Description |
| --- | --- |
| `ValueError` | If no checkpointer is set or no updates are provided. |
| `InvalidUpdateError` | If an invalid update is provided. |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | The updated config. |
### abulk\_update\_state `async` [¶](#langgraph.graph.state.CompiledStateGraph.abulk_update_state "Permanent link")
```
abulk_update_state(
    config: RunnableConfig,
    supersteps: Sequence[Sequence[StateUpdate]],
) -> RunnableConfig
```
Asynchronously apply updates to the graph state in bulk. Requires a checkpointer to be set.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to apply the updates to. | *required* |
| `supersteps` | `Sequence[Sequence[StateUpdate]]` | A list of supersteps, each including a list of updates to apply sequentially to a graph state. Each update is a tuple of the form `(values, as_node, task_id)` where task\_id is optional. | *required* |
Raises:
| Type | Description |
| --- | --- |
| `ValueError` | If no checkpointer is set or no updates are provided. |
| `InvalidUpdateError` | If an invalid update is provided. |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | The updated config. |
### get\_graph [¶](#langgraph.graph.state.CompiledStateGraph.get_graph "Permanent link")
```
get_graph(
    config: RunnableConfig | None = None,
    *,
    xray: int | bool = False
) -> Graph
```
Return a drawable representation of the computation graph.
### aget\_graph `async` [¶](#langgraph.graph.state.CompiledStateGraph.aget_graph "Permanent link")
```
aget_graph(
    config: RunnableConfig | None = None,
    *,
    xray: int | bool = False
) -> Graph
```
Return a drawable representation of the computation graph.
### get\_subgraphs [¶](#langgraph.graph.state.CompiledStateGraph.get_subgraphs "Permanent link")
```
get_subgraphs(
    *, namespace: str | None = None, recurse: bool = False
) -> Iterator[tuple[str, PregelProtocol]]
```
Get the subgraphs of the graph.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `str | None` | The namespace to filter the subgraphs by. | `None` |
| `recurse` | `bool` | Whether to recurse into the subgraphs. If False, only the immediate subgraphs will be returned. | `False` |
Returns:
| Type | Description |
| --- | --- |
| `Iterator[tuple[str, PregelProtocol]]` | Iterator[tuple[str, PregelProtocol]]: An iterator of the (namespace, subgraph) pairs. |
### aget\_subgraphs `async` [¶](#langgraph.graph.state.CompiledStateGraph.aget_subgraphs "Permanent link")
```
aget_subgraphs(
    *, namespace: str | None = None, recurse: bool = False
) -> AsyncIterator[tuple[str, PregelProtocol]]
```
Get the subgraphs of the graph.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `str | None` | The namespace to filter the subgraphs by. | `None` |
| `recurse` | `bool` | Whether to recurse into the subgraphs. If False, only the immediate subgraphs will be returned. | `False` |
Returns:
| Type | Description |
| --- | --- |
| `AsyncIterator[tuple[str, PregelProtocol]]` | AsyncIterator[tuple[str, PregelProtocol]]: An iterator of the (namespace, subgraph) pairs. |
### with\_config [¶](#langgraph.graph.state.CompiledStateGraph.with_config "Permanent link")
```
with_config(
    config: RunnableConfig | None = None, **kwargs: Any
) -> Self
```
Create a copy of the Pregel object with an updated config.
Functions:
| Name | Description |
| --- | --- |
| `add_messages` | Merges two lists of messages, updating existing messages by ID. |
## add\_messages [¶](#langgraph.graph.message.add_messages "Permanent link")
```
add_messages(
    left: Messages,
    right: Messages,
    *,
    format: Literal["langchain-openai"] | None = None
) -> Messages
```
Merges two lists of messages, updating existing messages by ID.
By default, this ensures the state is "append-only", unless the
new message has the same ID as an existing message.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `left` | `Messages` | The base list of messages. | *required* |
| `right` | `Messages` | The list of messages (or single message) to merge into the base list. | *required* |
| `format` | `Literal['langchain-openai'] | None` | The format to return messages in. If None then messages will be returned as is. If 'langchain-openai' then messages will be returned as BaseMessage objects with their contents formatted to match OpenAI message format, meaning contents can be string, 'text' blocks, or 'image\_url' blocks and tool responses are returned as their own ToolMessages.  Requirement  Must have `langchain-core>=0.3.11` installed to use this feature. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Messages` | A new list of messages with the messages from `right` merged into `left`. |
| `Messages` | If a message in `right` has the same ID as a message in `left`, the |
| `Messages` | message from `right` will replace the message from `left`. |
Example
Basic usage
```
from langchain_core.messages import AIMessage, HumanMessage
msgs1 = [HumanMessage(content="Hello", id="1")]
msgs2 = [AIMessage(content="Hi there!", id="2")]
add_messages(msgs1, msgs2)
# [HumanMessage(content='Hello', id='1'), AIMessage(content='Hi there!', id='2')]
```
Overwrite existing message
```
msgs1 = [HumanMessage(content="Hello", id="1")]
msgs2 = [HumanMessage(content="Hello again", id="1")]
add_messages(msgs1, msgs2)
# [HumanMessage(content='Hello again', id='1')]
```
Use in a StateGraph
```
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph
class State(TypedDict):
    messages: Annotated[list, add_messages]
builder = StateGraph(State)
builder.add_node("chatbot", lambda state: {"messages": [("assistant", "Hello")]})
builder.set_entry_point("chatbot")
builder.set_finish_point("chatbot")
graph = builder.compile()
graph.invoke({})
# {'messages': [AIMessage(content='Hello', id=...)]}
```
Use OpenAI message format
```
from typing import Annotated
from typing_extensions import TypedDict
from langgraph.graph import StateGraph, add_messages
class State(TypedDict):
    messages: Annotated[list, add_messages(format='langchain-openai')]
def chatbot_node(state: State) -> list:
    return {"messages": [
        {
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": "Here's an image:",
                    "cache_control": {"type": "ephemeral"},
                },
                {
                    "type": "image",
                    "source": {
                        "type": "base64",
                        "media_type": "image/jpeg",
                        "data": "1234",
                    },
                },
            ]
        },
    ]}
builder = StateGraph(State)
builder.add_node("chatbot", chatbot_node)
builder.set_entry_point("chatbot")
builder.set_finish_point("chatbot")
graph = builder.compile()
graph.invoke({"messages": []})
# {
#     'messages': [
#         HumanMessage(
#             content=[
#                 {"type": "text", "text": "Here's an image:"},
#                 {
#                     "type": "image_url",
#                     "image_url": {"url": "data:image/jpeg;base64,1234"},
#                 },
#             ],
#         ),
#     ]
# }
```
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/graphs/)
