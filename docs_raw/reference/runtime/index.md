# Runtime

# Runtime[¶](#runtime "Permanent link")
## Runtime `dataclass` [¶](#langgraph.runtime.Runtime "Permanent link")
Bases: `Generic[ContextT]`
Convenience class that bundles run-scoped context and other runtime utilities.
Added in version v0.6.0
Example:
```
from typing import TypedDict
from langgraph.graph import StateGraph
from dataclasses import dataclass
from langgraph.runtime import Runtime
from langgraph.store.memory import InMemoryStore
@dataclass
class Context:  # (1)!
    user_id: str
class State(TypedDict, total=False):
    response: str
store = InMemoryStore()  # (2)!
store.put(("users",), "user_123", {"name": "Alice"})
def personalized_greeting(state: State, runtime: Runtime[Context]) -> State:
    '''Generate personalized greeting using runtime context and store.'''
    user_id = runtime.context.user_id  # (3)!
    name = "unknown_user"
    if runtime.store:
        if memory := runtime.store.get(("users",), user_id):
            name = memory.value["name"]
    response = f"Hello {name}! Nice to see you again."
    return {"response": response}
graph = (
    StateGraph(state_schema=State, context_schema=Context)
    .add_node("personalized_greeting", personalized_greeting)
    .set_entry_point("personalized_greeting")
    .set_finish_point("personalized_greeting")
    .compile(store=store)
)
result = graph.invoke({}, context=Context(user_id="user_123"))
print(result)
# > {'response': 'Hello Alice! Nice to see you again.'}
```
1. Define a schema for the runtime context.
2. Create a store to persist memories and other information.
3. Use the runtime context to access the user\_id.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `context` | `ContextT` | Static context for the graph run, like user\_id, db\_conn, etc. |
| `store` | `BaseStore | None` | Store for the graph run, enabling persistence and memory. |
| `stream_writer` | `StreamWriter` | Function that writes to the custom stream. |
| `previous` | `Any` | The previous return value for the given thread. |
### context `class-attribute` `instance-attribute` [¶](#langgraph.runtime.Runtime.context "Permanent link")
```
context: ContextT = field(default=None)
```
Static context for the graph run, like user\_id, db\_conn, etc.
Can also be thought of as 'run dependencies'.
### store `class-attribute` `instance-attribute` [¶](#langgraph.runtime.Runtime.store "Permanent link")
```
store: BaseStore | None = field(default=None)
```
Store for the graph run, enabling persistence and memory.
### stream\_writer `class-attribute` `instance-attribute` [¶](#langgraph.runtime.Runtime.stream_writer "Permanent link")
```
stream_writer: StreamWriter = field(
    default=_no_op_stream_writer
)
```
Function that writes to the custom stream.
### previous `class-attribute` `instance-attribute` [¶](#langgraph.runtime.Runtime.previous "Permanent link")
```
previous: Any = field(default=None)
```
The previous return value for the given thread.
Only available with the functional API when a checkpointer is provided.
Functions:
| Name | Description |
| --- | --- |
| `get_runtime` | Get the runtime for the current graph run. |
## get\_runtime [¶](#langgraph.runtime.get_runtime "Permanent link")
```
get_runtime(
    context_schema: type[ContextT] | None = None,
) -> Runtime[ContextT]
```
Get the runtime for the current graph run.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `context_schema` | `type[ContextT] | None` | Optional schema used for type hinting the return type of the runtime. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Runtime[ContextT]` | The runtime for the current graph run. |
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/runtime/)
