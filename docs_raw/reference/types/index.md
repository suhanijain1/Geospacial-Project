# Types

# Types[¶](#types "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `RetryPolicy` | Configuration for retrying nodes. |
| `CachePolicy` | Configuration for caching nodes. |
| `Interrupt` | Information about an interrupt that occurred in a node. |
| `PregelTask` | A Pregel task. |
| `StateSnapshot` | Snapshot of the state of the graph at the beginning of a step. |
| `Send` | A message or packet to send to a specific node in the graph. |
| `Command` | One or more commands to update the graph's state and send messages to nodes. |
Functions:
| Name | Description |
| --- | --- |
| `interrupt` | Interrupt the graph with a resumable exception from within a node. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `All` |  | Special value to indicate that graph should interrupt on all nodes. |
| `StreamMode` |  | How the stream method should emit outputs. |
| `StreamWriter` |  | Callable that accepts a single argument and writes it to the output stream. |
## All `module-attribute` [¶](#langgraph.types.All "Permanent link")
```
All = Literal['*']
```
Special value to indicate that graph should interrupt on all nodes.
## StreamMode `module-attribute` [¶](#langgraph.types.StreamMode "Permanent link")
```
StreamMode = Literal[
    "values",
    "updates",
    "checkpoints",
    "tasks",
    "debug",
    "messages",
    "custom",
]
```
How the stream method should emit outputs.
* `"values"`: Emit all values in the state after each step, including interrupts.
  When used with functional API, values are emitted once at the end of the workflow.
* `"updates"`: Emit only the node or task names and updates returned by the nodes or tasks after each step.
  If multiple updates are made in the same step (e.g. multiple nodes are run) then those updates are emitted separately.
* `"custom"`: Emit custom data using from inside nodes or tasks using `StreamWriter`.
* `"messages"`: Emit LLM messages token-by-token together with metadata for any LLM invocations inside nodes or tasks.
* `"checkpoints"`: Emit an event when a checkpoint is created, in the same format as returned by get\_state().
* `"tasks"`: Emit events when tasks start and finish, including their results and errors.
* `"debug"`: Emit "checkpoints" and "tasks" events, for debugging purposes.
## StreamWriter `module-attribute` [¶](#langgraph.types.StreamWriter "Permanent link")
```
StreamWriter = Callable[[Any], None]
```
Callable that accepts a single argument and writes it to the output stream.
Always injected into nodes if requested as a keyword argument, but it's a no-op
when not using stream\_mode="custom".
## RetryPolicy [¶](#langgraph.types.RetryPolicy "Permanent link")
Bases: `NamedTuple`
Configuration for retrying nodes.
Added in version 0.2.24.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `initial_interval` | `float` | Amount of time that must elapse before the first retry occurs. In seconds. |
| `backoff_factor` | `float` | Multiplier by which the interval increases after each retry. |
| `max_interval` | `float` | Maximum amount of time that may elapse between retries. In seconds. |
| `max_attempts` | `int` | Maximum number of attempts to make before giving up, including the first. |
| `jitter` | `bool` | Whether to add random jitter to the interval between retries. |
| `retry_on` | `type[Exception] | Sequence[type[Exception]] | Callable[[Exception], bool]` | List of exception classes that should trigger a retry, or a callable that returns True for exceptions that should trigger a retry. |
### initial\_interval `class-attribute` `instance-attribute` [¶](#langgraph.types.RetryPolicy.initial_interval "Permanent link")
```
initial_interval: float = 0.5
```
Amount of time that must elapse before the first retry occurs. In seconds.
### backoff\_factor `class-attribute` `instance-attribute` [¶](#langgraph.types.RetryPolicy.backoff_factor "Permanent link")
```
backoff_factor: float = 2.0
```
Multiplier by which the interval increases after each retry.
### max\_interval `class-attribute` `instance-attribute` [¶](#langgraph.types.RetryPolicy.max_interval "Permanent link")
```
max_interval: float = 128.0
```
Maximum amount of time that may elapse between retries. In seconds.
### max\_attempts `class-attribute` `instance-attribute` [¶](#langgraph.types.RetryPolicy.max_attempts "Permanent link")
```
max_attempts: int = 3
```
Maximum number of attempts to make before giving up, including the first.
### jitter `class-attribute` `instance-attribute` [¶](#langgraph.types.RetryPolicy.jitter "Permanent link")
```
jitter: bool = True
```
Whether to add random jitter to the interval between retries.
### retry\_on `class-attribute` `instance-attribute` [¶](#langgraph.types.RetryPolicy.retry_on "Permanent link")
```
retry_on: (
    type[Exception]
    | Sequence[type[Exception]]
    | Callable[[Exception], bool]
) = default_retry_on
```
List of exception classes that should trigger a retry, or a callable that returns True for exceptions that should trigger a retry.
## CachePolicy `dataclass` [¶](#langgraph.types.CachePolicy "Permanent link")
Bases: `Generic[KeyFuncT]`
Configuration for caching nodes.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `key_func` | `KeyFuncT` | Function to generate a cache key from the node's input. |
| `ttl` | `int | None` | Time to live for the cache entry in seconds. If None, the entry never expires. |
### key\_func `class-attribute` `instance-attribute` [¶](#langgraph.types.CachePolicy.key_func "Permanent link")
```
key_func: KeyFuncT = default_cache_key
```
Function to generate a cache key from the node's input.
Defaults to hashing the input with pickle.
### ttl `class-attribute` `instance-attribute` [¶](#langgraph.types.CachePolicy.ttl "Permanent link")
```
ttl: int | None = None
```
Time to live for the cache entry in seconds. If None, the entry never expires.
## Interrupt `dataclass` [¶](#langgraph.types.Interrupt "Permanent link")
Information about an interrupt that occurred in a node.
Added in version 0.2.24.
Changed in version v0.4.0
* `interrupt_id` was introduced as a property
Changed in version v0.6.0
The following attributes have been removed:
* `ns`
* `when`
* `resumable`
* `interrupt_id`, deprecated in favor of `id`
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `id` | `str` | The ID of the interrupt. Can be used to resume the interrupt directly. |
| `value` | `Any` | The value associated with the interrupt. |
### id `instance-attribute` [¶](#langgraph.types.Interrupt.id "Permanent link")
```
id: str
```
The ID of the interrupt. Can be used to resume the interrupt directly.
### value `instance-attribute` [¶](#langgraph.types.Interrupt.value "Permanent link")
```
value: Any = value
```
The value associated with the interrupt.
## PregelTask [¶](#langgraph.types.PregelTask "Permanent link")
Bases: `NamedTuple`
A Pregel task.
## StateSnapshot [¶](#langgraph.types.StateSnapshot "Permanent link")
Bases: `NamedTuple`
Snapshot of the state of the graph at the beginning of a step.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `values` | `dict[str, Any] | Any` | Current values of channels. |
| `next` | `tuple[str, ...]` | The name of the node to execute in each task for this step. |
| `config` | `RunnableConfig` | Config used to fetch this snapshot. |
| `metadata` | `CheckpointMetadata | None` | Metadata associated with this snapshot. |
| `created_at` | `str | None` | Timestamp of snapshot creation. |
| `parent_config` | `RunnableConfig | None` | Config used to fetch the parent snapshot, if any. |
| `tasks` | `tuple[PregelTask, ...]` | Tasks to execute in this step. If already attempted, may contain an error. |
| `interrupts` | `tuple[Interrupt, ...]` | Interrupts that occurred in this step that are pending resolution. |
### values `instance-attribute` [¶](#langgraph.types.StateSnapshot.values "Permanent link")
```
values: dict[str, Any] | Any
```
Current values of channels.
### next `instance-attribute` [¶](#langgraph.types.StateSnapshot.next "Permanent link")
```
next: tuple[str, ...]
```
The name of the node to execute in each task for this step.
### config `instance-attribute` [¶](#langgraph.types.StateSnapshot.config "Permanent link")
```
config: RunnableConfig
```
Config used to fetch this snapshot.
### metadata `instance-attribute` [¶](#langgraph.types.StateSnapshot.metadata "Permanent link")
```
metadata: CheckpointMetadata | None
```
Metadata associated with this snapshot.
### created\_at `instance-attribute` [¶](#langgraph.types.StateSnapshot.created_at "Permanent link")
```
created_at: str | None
```
Timestamp of snapshot creation.
### parent\_config `instance-attribute` [¶](#langgraph.types.StateSnapshot.parent_config "Permanent link")
```
parent_config: RunnableConfig | None
```
Config used to fetch the parent snapshot, if any.
### tasks `instance-attribute` [¶](#langgraph.types.StateSnapshot.tasks "Permanent link")
```
tasks: tuple[PregelTask, ...]
```
Tasks to execute in this step. If already attempted, may contain an error.
### interrupts `instance-attribute` [¶](#langgraph.types.StateSnapshot.interrupts "Permanent link")
```
interrupts: tuple[Interrupt, ...]
```
Interrupts that occurred in this step that are pending resolution.
## Send [¶](#langgraph.types.Send "Permanent link")
A message or packet to send to a specific node in the graph.
The `Send` class is used within a `StateGraph`'s conditional edges to
dynamically invoke a node with a custom state at the next step.
Importantly, the sent state can differ from the core graph's state,
allowing for flexible and dynamic workflow management.
One such example is a "map-reduce" workflow where your graph invokes
the same node multiple times in parallel with different states,
before aggregating the results back into the main graph's state.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `node` | `str` | The name of the target node to send the message to. |
| `arg` | `Any` | The state or message to send to the target node. |
Examples:
```
>>> from typing import Annotated
>>> import operator
>>> class OverallState(TypedDict):
...     subjects: list[str]
...     jokes: Annotated[list[str], operator.add]
...
>>> from langgraph.types import Send
>>> from langgraph.graph import END, START
>>> def continue_to_jokes(state: OverallState):
...     return [Send("generate_joke", {"subject": s}) for s in state['subjects']]
...
>>> from langgraph.graph import StateGraph
>>> builder = StateGraph(OverallState)
>>> builder.add_node("generate_joke", lambda state: {"jokes": [f"Joke about {state['subject']}"]})
>>> builder.add_conditional_edges(START, continue_to_jokes)
>>> builder.add_edge("generate_joke", END)
>>> graph = builder.compile()
>>>
>>> # Invoking with two subjects results in a generated joke for each
>>> graph.invoke({"subjects": ["cats", "dogs"]})
{'subjects': ['cats', 'dogs'], 'jokes': ['Joke about cats', 'Joke about dogs']}
```
Methods:
| Name | Description |
| --- | --- |
| `__init__` | Initialize a new instance of the Send class. |
### \_\_init\_\_ [¶](#langgraph.types.Send.__init__ "Permanent link")
```
__init__(node: str, arg: Any) -> None
```
Initialize a new instance of the Send class.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `node` | `str` | The name of the target node to send the message to. | *required* |
| `arg` | `Any` | The state or message to send to the target node. | *required* |
## Command `dataclass` [¶](#langgraph.types.Command "Permanent link")
Bases: `Generic[N]`, `ToolOutputMixin`
One or more commands to update the graph's state and send messages to nodes.
Added in version 0.2.24.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `graph` | `str | None` | graph to send the command to. Supported values are:   * None: the current graph (default) * Command.PARENT: closest parent graph | `None` |
| `update` | `Any | None` | update to apply to the graph's state. | `None` |
| `resume` | `dict[str, Any] | Any | None` | value to resume execution with. To be used together with [`interrupt()`](#langgraph.types.interrupt "<code class=\"doc-symbol doc-symbol-heading doc-symbol-function\"></code>            <span class=\"doc doc-object-name doc-function-name\">interrupt</span>"). Can be one of the following:   * mapping of interrupt ids to resume values * a single value with which to resume the next interrupt | `None` |
| `goto` | `Send | Sequence[Send | N] | N` | can be one of the following:   * name of the node to navigate to next (any node that belongs to the specified `graph`) * sequence of node names to navigate to next * `Send` object (to execute a node with the input provided) * sequence of `Send` objects | `()` |
## interrupt [¶](#langgraph.types.interrupt "Permanent link")
```
interrupt(value: Any) -> Any
```
Interrupt the graph with a resumable exception from within a node.
The `interrupt` function enables human-in-the-loop workflows by pausing graph
execution and surfacing a value to the client. This value can communicate context
or request input required to resume execution.
In a given node, the first invocation of this function raises a `GraphInterrupt`
exception, halting execution. The provided `value` is included with the exception
and sent to the client executing the graph.
A client resuming the graph must use the [`Command`](#langgraph.types.Command "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">Command</span>
  <span class=\"doc doc-labels\">
      <small class=\"doc doc-label doc-label-dataclass\"><code>dataclass</code></small>
  </span>")
primitive to specify a value for the interrupt and continue execution.
The graph resumes from the start of the node, **re-executing** all logic.
If a node contains multiple `interrupt` calls, LangGraph matches resume values
to interrupts based on their order in the node. This list of resume values
is scoped to the specific task executing the node and is not shared across tasks.
To use an `interrupt`, you must enable a checkpointer, as the feature relies
on persisting the graph state.
Example
```
import uuid
from typing import Optional
from typing_extensions import TypedDict
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.constants import START
from langgraph.graph import StateGraph
from langgraph.types import interrupt, Command
class State(TypedDict):
    """The graph state."""
    foo: str
    human_value: Optional[str]
    """Human value will be updated using an interrupt."""
def node(state: State):
    answer = interrupt(
        # This value will be sent to the client
        # as part of the interrupt information.
        "what is your age?"
    )
    print(f"> Received an input from the interrupt: {answer}")
    return {"human_value": answer}
builder = StateGraph(State)
builder.add_node("node", node)
builder.add_edge(START, "node")
# A checkpointer must be enabled for interrupts to work!
checkpointer = InMemorySaver()
graph = builder.compile(checkpointer=checkpointer)
config = {
    "configurable": {
        "thread_id": uuid.uuid4(),
    }
}
for chunk in graph.stream({"foo": "abc"}, config):
    print(chunk)
# > {'__interrupt__': (Interrupt(value='what is your age?', id='45fda8478b2ef754419799e10992af06'),)}
command = Command(resume="some input from a human!!!")
for chunk in graph.stream(Command(resume="some input from a human!!!"), config):
    print(chunk)
# > Received an input from the interrupt: some input from a human!!!
# > {'node': {'human_value': 'some input from a human!!!'}}
```
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `value` | `Any` | The value to surface to the client when the graph is interrupted. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `Any` | `Any` | On subsequent invocations within the same node (same task to be precise), returns the value provided during the first invocation |
Raises:
| Type | Description |
| --- | --- |
| `GraphInterrupt` | On the first invocation within the node, halts execution and surfaces the provided value to the client. |
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/types/)
