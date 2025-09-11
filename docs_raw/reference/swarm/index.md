# Swarm

# LangGraph Swarm[¶](#langgraph-swarm "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `SwarmState` | State schema for the multi-agent swarm. |
Functions:
| Name | Description |
| --- | --- |
| `create_swarm` | Create a multi-agent swarm. |
| `add_active_agent_router` | Add a router to the currently active agent to the StateGraph. |
## SwarmState [¶](#langgraph_swarm.swarm.SwarmState "Permanent link")
Bases: `MessagesState`
State schema for the multi-agent swarm.
## create\_swarm [¶](#langgraph_swarm.swarm.create_swarm "Permanent link")
```
create_swarm(
    agents: list[Pregel],
    *,
    default_active_agent: str,
    state_schema: StateSchemaType = SwarmState,
    config_schema: type[Any] | None = None
) -> StateGraph
```
Create a multi-agent swarm.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `agents` | `list[Pregel]` | List of agents to add to the swarm An agent can be a LangGraph [CompiledStateGraph](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.CompiledStateGraph), a functional API [workflow](https://langchain-ai.github.io/langgraph/reference/func/#langgraph.func.entrypoint), or any other [Pregel](https://langchain-ai.github.io/langgraph/reference/pregel/#langgraph.pregel.Pregel) object. | *required* |
| `default_active_agent` | `str` | Name of the agent to route to by default (if no agents are currently active). | *required* |
| `state_schema` | `StateSchemaType` | State schema to use for the multi-agent graph. | `SwarmState` |
| `config_schema` | `type[Any] | None` | An optional schema for configuration. Use this to expose configurable parameters via `swarm.config_specs`. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `StateGraph` | A multi-agent swarm StateGraph. |
Example
```
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph_swarm import create_handoff_tool, create_swarm
def add(a: int, b: int) -> int:
    '''Add two numbers'''
    return a + b
alice = create_react_agent(
    "openai:gpt-4o",
    [add, create_handoff_tool(agent_name="Bob")],
    prompt="You are Alice, an addition expert.",
    name="Alice",
)
bob = create_react_agent(
    "openai:gpt-4o",
    [create_handoff_tool(agent_name="Alice", description="Transfer to Alice, she can help with math")],
    prompt="You are Bob, you speak like a pirate.",
    name="Bob",
)
checkpointer = InMemorySaver()
workflow = create_swarm(
    [alice, bob],
    default_active_agent="Alice"
)
app = workflow.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}
turn_1 = app.invoke(
    {"messages": [{"role": "user", "content": "i'd like to speak to Bob"}]},
    config,
)
turn_2 = app.invoke(
    {"messages": [{"role": "user", "content": "what's 5 + 7?"}]},
    config,
)
```
## add\_active\_agent\_router [¶](#langgraph_swarm.swarm.add_active_agent_router "Permanent link")
```
add_active_agent_router(
    builder: StateGraph,
    *,
    route_to: list[str],
    default_active_agent: str
) -> StateGraph
```
Add a router to the currently active agent to the StateGraph.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `builder` | `StateGraph` | The graph builder (StateGraph) to add the router to. | *required* |
| `route_to` | `list[str]` | A list of agent (node) names to route to. | *required* |
| `default_active_agent` | `str` | Name of the agent to route to by default (if no agents are currently active). | *required* |
Returns:
| Type | Description |
| --- | --- |
| `StateGraph` | StateGraph with the router added. |
Example
```
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.prebuilt import create_react_agent
from langgraph.graph import StateGraph
from langgraph_swarm import SwarmState, create_handoff_tool, add_active_agent_router
def add(a: int, b: int) -> int:
    '''Add two numbers'''
    return a + b
alice = create_react_agent(
    "openai:gpt-4o",
    [add, create_handoff_tool(agent_name="Bob")],
    prompt="You are Alice, an addition expert.",
    name="Alice",
)
bob = create_react_agent(
    "openai:gpt-4o",
    [create_handoff_tool(agent_name="Alice", description="Transfer to Alice, she can help with math")],
    prompt="You are Bob, you speak like a pirate.",
    name="Bob",
)
checkpointer = InMemorySaver()
workflow = (
    StateGraph(SwarmState)
    .add_node(alice, destinations=("Bob",))
    .add_node(bob, destinations=("Alice",))
)
# this is the router that enables us to keep track of the last active agent
workflow = add_active_agent_router(
    builder=workflow,
    route_to=["Alice", "Bob"],
    default_active_agent="Alice",
)
# compile the workflow
app = workflow.compile(checkpointer=checkpointer)
config = {"configurable": {"thread_id": "1"}}
turn_1 = app.invoke(
    {"messages": [{"role": "user", "content": "i'd like to speak to Bob"}]},
    config,
)
turn_2 = app.invoke(
    {"messages": [{"role": "user", "content": "what's 5 + 7?"}]},
    config,
)
```
Functions:
| Name | Description |
| --- | --- |
| `create_handoff_tool` | Create a tool that can handoff control to the requested agent. |
## create\_handoff\_tool [¶](#langgraph_swarm.handoff.create_handoff_tool "Permanent link")
```
create_handoff_tool(
    *,
    agent_name: str,
    name: str | None = None,
    description: str | None = None
) -> BaseTool
```
Create a tool that can handoff control to the requested agent.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `agent_name` | `str` | The name of the agent to handoff control to, i.e. the name of the agent node in the multi-agent graph. Agent names should be simple, clear and unique, preferably in snake\_case, although you are only limited to the names accepted by LangGraph nodes as well as the tool names accepted by LLM providers (the tool name will look like this: `transfer_to_<agent_name>`). | *required* |
| `name` | `str | None` | Optional name of the tool to use for the handoff. If not provided, the tool name will be `transfer_to_<agent_name>`. | `None` |
| `description` | `str | None` | Optional description for the handoff tool. If not provided, the tool description will be `Ask agent <agent_name> for help`. | `None` |
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/swarm/)
