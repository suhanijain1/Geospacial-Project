# Pregel

# Pregel[¶](#pregel "Permanent link")
## NodeBuilder [¶](#langgraph.pregel.NodeBuilder "Permanent link")
Methods:
| Name | Description |
| --- | --- |
| `subscribe_only` | Subscribe to a single channel. |
| `subscribe_to` | Add channels to subscribe to. Node will be invoked when any of these |
| `read_from` | Adds the specified channels to read from, without subscribing to them. |
| `do` | Adds the specified node. |
| `write_to` | Add channel writes. |
| `meta` | Add tags or metadata to the node. |
| `build` | Builds the node. |
### subscribe\_only [¶](#langgraph.pregel.NodeBuilder.subscribe_only "Permanent link")
```
subscribe_only(channel: str) -> Self
```
Subscribe to a single channel.
### subscribe\_to [¶](#langgraph.pregel.NodeBuilder.subscribe_to "Permanent link")
```
subscribe_to(*channels: str, read: bool = True) -> Self
```
Add channels to subscribe to. Node will be invoked when any of these
channels are updated, with a dict of the channel values as input.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `channels` | `str` | Channel name(s) to subscribe to | `()` |
| `read` | `bool` | If True, the channels will be included in the input to the node. Otherwise, they will trigger the node without being sent in input. | `True` |
Returns:
| Type | Description |
| --- | --- |
| `Self` | Self for chaining |
### read\_from [¶](#langgraph.pregel.NodeBuilder.read_from "Permanent link")
```
read_from(*channels: str) -> Self
```
Adds the specified channels to read from, without subscribing to them.
### do [¶](#langgraph.pregel.NodeBuilder.do "Permanent link")
```
do(node: RunnableLike) -> Self
```
Adds the specified node.
### write\_to [¶](#langgraph.pregel.NodeBuilder.write_to "Permanent link")
```
write_to(
    *channels: str | ChannelWriteEntry,
    **kwargs: _WriteValue
) -> Self
```
Add channel writes.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `*channels` | `str | ChannelWriteEntry` | Channel names to write to | `()` |
| `**kwargs` | `_WriteValue` | Channel name and value mappings | `{}` |
Returns:
| Type | Description |
| --- | --- |
| `Self` | Self for chaining |
### meta [¶](#langgraph.pregel.NodeBuilder.meta "Permanent link")
```
meta(*tags: str, **metadata: Any) -> Self
```
Add tags or metadata to the node.
### build [¶](#langgraph.pregel.NodeBuilder.build "Permanent link")
```
build() -> PregelNode
```
Builds the node.
## Pregel [¶](#langgraph.pregel.Pregel "Permanent link")
Bases: `PregelProtocol[StateT, ContextT, InputT, OutputT]`, `Generic[StateT, ContextT, InputT, OutputT]`
Pregel manages the runtime behavior for LangGraph applications.
#### Overview[¶](#langgraph.pregel.Pregel--overview "Permanent link")
Pregel combines [**actors**](https://en.wikipedia.org/wiki/Actor_model)
and **channels** into a single application.
**Actors** read data from channels and write data to channels.
Pregel organizes the execution of the application into multiple steps,
following the **Pregel Algorithm**/**Bulk Synchronous Parallel** model.
Each step consists of three phases:
* **Plan**: Determine which **actors** to execute in this step. For example,
  in the first step, select the **actors** that subscribe to the special
  **input** channels; in subsequent steps,
  select the **actors** that subscribe to channels updated in the previous step.
* **Execution**: Execute all selected **actors** in parallel,
  until all complete, or one fails, or a timeout is reached. During this
  phase, channel updates are invisible to actors until the next step.
* **Update**: Update the channels with the values written by the **actors**
  in this step.
Repeat until no **actors** are selected for execution, or a maximum number of
steps is reached.
#### Actors[¶](#langgraph.pregel.Pregel--actors "Permanent link")
An **actor** is a `PregelNode`.
It subscribes to channels, reads data from them, and writes data to them.
It can be thought of as an **actor** in the Pregel algorithm.
`PregelNodes` implement LangChain's
Runnable interface.
#### Channels[¶](#langgraph.pregel.Pregel--channels "Permanent link")
Channels are used to communicate between actors (`PregelNodes`).
Each channel has a value type, an update type, and an update function – which
takes a sequence of updates and
modifies the stored value. Channels can be used to send data from one chain to
another, or to send data from a chain to itself in a future step. LangGraph
provides a number of built-in channels:
##### Basic channels: LastValue and Topic[¶](#langgraph.pregel.Pregel--basic-channels-lastvalue-and-topic "Permanent link")
* `LastValue`: The default channel, stores the last value sent to the channel,
  useful for input and output values, or for sending data from one step to the next
* `Topic`: A configurable PubSub Topic, useful for sending multiple values
  between *actors*, or for accumulating output. Can be configured to deduplicate
  values, and/or to accumulate values over the course of multiple steps.
##### Advanced channels: Context and BinaryOperatorAggregate[¶](#langgraph.pregel.Pregel--advanced-channels-context-and-binaryoperatoraggregate "Permanent link")
* `Context`: exposes the value of a context manager, managing its lifecycle.
  Useful for accessing external resources that require setup and/or teardown. eg.
  `client = Context(httpx.Client)`
* `BinaryOperatorAggregate`: stores a persistent value, updated by applying
  a binary operator to the current value and each update
  sent to the channel, useful for computing aggregates over multiple steps. eg.
  `total = BinaryOperatorAggregate(int, operator.add)`
#### Examples[¶](#langgraph.pregel.Pregel--examples "Permanent link")
Most users will interact with Pregel via a
[StateGraph (Graph API)](../graphs/#langgraph.graph.state.StateGraph "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">StateGraph</span>") or via an
[entrypoint (Functional API)](../func/#langgraph.func.entrypoint "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">entrypoint</span>").
However, for **advanced** use cases, Pregel can be used directly. If you're
not sure whether you need to use Pregel directly, then the answer is probably no
– you should use the Graph API or Functional API instead. These are higher-level
interfaces that will compile down to Pregel under the hood.
Here are some examples to give you a sense of how it works:
Single node application
```
from langgraph.channels import EphemeralValue
from langgraph.pregel import Pregel, NodeBuilder
node1 = (
    NodeBuilder().subscribe_only("a")
    .do(lambda x: x + x)
    .write_to("b")
)
app = Pregel(
    nodes={"node1": node1},
    channels={
        "a": EphemeralValue(str),
        "b": EphemeralValue(str),
    },
    input_channels=["a"],
    output_channels=["b"],
)
app.invoke({"a": "foo"})
```
```
{'b': 'foofoo'}
```
Using multiple nodes and multiple output channels
```
from langgraph.channels import LastValue, EphemeralValue
from langgraph.pregel import Pregel, NodeBuilder
node1 = (
    NodeBuilder().subscribe_only("a")
    .do(lambda x: x + x)
    .write_to("b")
)
node2 = (
    NodeBuilder().subscribe_to("b")
    .do(lambda x: x["b"] + x["b"])
    .write_to("c")
)
app = Pregel(
    nodes={"node1": node1, "node2": node2},
    channels={
        "a": EphemeralValue(str),
        "b": LastValue(str),
        "c": EphemeralValue(str),
    },
    input_channels=["a"],
    output_channels=["b", "c"],
)
app.invoke({"a": "foo"})
```
```
{'b': 'foofoo', 'c': 'foofoofoofoo'}
```
Using a Topic channel
```
from langgraph.channels import LastValue, EphemeralValue, Topic
from langgraph.pregel import Pregel, NodeBuilder
node1 = (
    NodeBuilder().subscribe_only("a")
    .do(lambda x: x + x)
    .write_to("b", "c")
)
node2 = (
    NodeBuilder().subscribe_only("b")
    .do(lambda x: x + x)
    .write_to("c")
)
app = Pregel(
    nodes={"node1": node1, "node2": node2},
    channels={
        "a": EphemeralValue(str),
        "b": EphemeralValue(str),
        "c": Topic(str, accumulate=True),
    },
    input_channels=["a"],
    output_channels=["c"],
)
app.invoke({"a": "foo"})
```
```
{'c': ['foofoo', 'foofoofoofoo']}
```
Using a BinaryOperatorAggregate channel
```
from langgraph.channels import EphemeralValue, BinaryOperatorAggregate
from langgraph.pregel import Pregel, NodeBuilder
node1 = (
    NodeBuilder().subscribe_only("a")
    .do(lambda x: x + x)
    .write_to("b", "c")
)
node2 = (
    NodeBuilder().subscribe_only("b")
    .do(lambda x: x + x)
    .write_to("c")
)
def reducer(current, update):
    if current:
        return current + " | " + update
    else:
        return update
app = Pregel(
    nodes={"node1": node1, "node2": node2},
    channels={
        "a": EphemeralValue(str),
        "b": EphemeralValue(str),
        "c": BinaryOperatorAggregate(str, operator=reducer),
    },
    input_channels=["a"],
    output_channels=["c"]
)
app.invoke({"a": "foo"})
```
```
{'c': 'foofoo | foofoofoofoo'}
```
Introducing a cycle
This example demonstrates how to introduce a cycle in the graph, by having
a chain write to a channel it subscribes to. Execution will continue
until a None value is written to the channel.
```
from langgraph.channels import EphemeralValue
from langgraph.pregel import Pregel, NodeBuilder, ChannelWriteEntry
example_node = (
    NodeBuilder().subscribe_only("value")
    .do(lambda x: x + x if len(x) < 10 else None)
    .write_to(ChannelWriteEntry(channel="value", skip_none=True))
)
app = Pregel(
    nodes={"example_node": example_node},
    channels={
        "value": EphemeralValue(str),
    },
    input_channels=["value"],
    output_channels=["value"]
)
app.invoke({"value": "a"})
```
```
{'value': 'aaaaaaaaaaaaaaaa'}
```
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
### stream [¶](#langgraph.pregel.Pregel.stream "Permanent link")
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
### astream `async` [¶](#langgraph.pregel.Pregel.astream "Permanent link")
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
### invoke [¶](#langgraph.pregel.Pregel.invoke "Permanent link")
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
### ainvoke `async` [¶](#langgraph.pregel.Pregel.ainvoke "Permanent link")
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
### get\_state [¶](#langgraph.pregel.Pregel.get_state "Permanent link")
```
get_state(
    config: RunnableConfig, *, subgraphs: bool = False
) -> StateSnapshot
```
Get the current state of the graph.
### aget\_state `async` [¶](#langgraph.pregel.Pregel.aget_state "Permanent link")
```
aget_state(
    config: RunnableConfig, *, subgraphs: bool = False
) -> StateSnapshot
```
Get the current state of the graph.
### get\_state\_history [¶](#langgraph.pregel.Pregel.get_state_history "Permanent link")
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
### aget\_state\_history `async` [¶](#langgraph.pregel.Pregel.aget_state_history "Permanent link")
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
### update\_state [¶](#langgraph.pregel.Pregel.update_state "Permanent link")
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
### aupdate\_state `async` [¶](#langgraph.pregel.Pregel.aupdate_state "Permanent link")
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
### bulk\_update\_state [¶](#langgraph.pregel.Pregel.bulk_update_state "Permanent link")
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
### abulk\_update\_state `async` [¶](#langgraph.pregel.Pregel.abulk_update_state "Permanent link")
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
### get\_graph [¶](#langgraph.pregel.Pregel.get_graph "Permanent link")
```
get_graph(
    config: RunnableConfig | None = None,
    *,
    xray: int | bool = False
) -> Graph
```
Return a drawable representation of the computation graph.
### aget\_graph `async` [¶](#langgraph.pregel.Pregel.aget_graph "Permanent link")
```
aget_graph(
    config: RunnableConfig | None = None,
    *,
    xray: int | bool = False
) -> Graph
```
Return a drawable representation of the computation graph.
### get\_subgraphs [¶](#langgraph.pregel.Pregel.get_subgraphs "Permanent link")
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
### aget\_subgraphs `async` [¶](#langgraph.pregel.Pregel.aget_subgraphs "Permanent link")
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
### with\_config [¶](#langgraph.pregel.Pregel.with_config "Permanent link")
```
with_config(
    config: RunnableConfig | None = None, **kwargs: Any
) -> Self
```
Create a copy of the Pregel object with an updated config.
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/pregel/)
