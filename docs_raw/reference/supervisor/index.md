# Supervisor

# LangGraph Supervisor[¶](#langgraph-supervisor "Permanent link")
Functions:
| Name | Description |
| --- | --- |
| `create_supervisor` | Create a multi-agent supervisor. |
## create\_supervisor [¶](#langgraph_supervisor.supervisor.create_supervisor "Permanent link")
```
create_supervisor(
    agents: list[Pregel],
    *,
    model: LanguageModelLike,
    tools: (
        list[BaseTool | Callable] | ToolNode | None
    ) = None,
    prompt: Prompt | None = None,
    response_format: Optional[
        Union[
            StructuredResponseSchema,
            tuple[str, StructuredResponseSchema],
        ]
    ] = None,
    pre_model_hook: Optional[RunnableLike] = None,
    post_model_hook: Optional[RunnableLike] = None,
    parallel_tool_calls: bool = False,
    state_schema: StateSchemaType | None = None,
    config_schema: Type[Any] | None = None,
    output_mode: OutputMode = "last_message",
    add_handoff_messages: bool = True,
    handoff_tool_prefix: Optional[str] = None,
    add_handoff_back_messages: Optional[bool] = None,
    supervisor_name: str = "supervisor",
    include_agent_name: AgentNameMode | None = None
) -> StateGraph
```
Create a multi-agent supervisor.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `agents` | `list[Pregel]` | List of agents to manage. An agent can be a LangGraph [CompiledStateGraph](https://langchain-ai.github.io/langgraph/reference/graphs/#langgraph.graph.state.CompiledStateGraph), a functional API [workflow](https://langchain-ai.github.io/langgraph/reference/func/#langgraph.func.entrypoint), or any other [Pregel](https://langchain-ai.github.io/langgraph/reference/pregel/#langgraph.pregel.Pregel) object. | *required* |
| `model` | `LanguageModelLike` | Language model to use for the supervisor | *required* |
| `tools` | `list[BaseTool | Callable] | ToolNode | None` | Tools to use for the supervisor | `None` |
| `prompt` | `Prompt | None` | Optional prompt to use for the supervisor. Can be one of:   * str: This is converted to a SystemMessage and added to the beginning of the list of messages in state["messages"]. * SystemMessage: this is added to the beginning of the list of messages in state["messages"]. * Callable: This function should take in full graph state and the output is then passed to the language model. * Runnable: This runnable should take in full graph state and the output is then passed to the language model. | `None` |
| `response_format` | `Optional[Union[StructuredResponseSchema, tuple[str, StructuredResponseSchema]]]` | An optional schema for the final supervisor output.  If provided, output will be formatted to match the given schema and returned in the 'structured\_response' state key. If not provided, `structured_response` will not be present in the output state. Can be passed in as:  ``` - an OpenAI function/tool schema, - a JSON Schema, - a TypedDict class, - or a Pydantic class. - a tuple (prompt, schema), where schema is one of the above.     The prompt will be used together with the model that is being used to generate the structured response. ```  Important  `response_format` requires the model to support `.with_structured_output`  Note  `response_format` requires `structured_response` key in your state schema. You can use the prebuilt `langgraph.prebuilt.chat_agent_executor.AgentStateWithStructuredResponse`. | `None` |
| `pre_model_hook` | `Optional[RunnableLike]` | An optional node to add before the LLM node in the supervisor agent (i.e., the node that calls the LLM). Useful for managing long message histories (e.g., message trimming, summarization, etc.). Pre-model hook must be a callable or a runnable that takes in current graph state and returns a state update in the form of ``` # At least one of `messages` or `llm_input_messages` MUST be provided {     # If provided, will UPDATE the `messages` in the state     "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), ...],     # If provided, will be used as the input to the LLM,     # and will NOT UPDATE `messages` in the state     "llm_input_messages": [...],     # Any other state keys that need to be propagated     ... } ```  Important  At least one of `messages` or `llm_input_messages` MUST be provided and will be used as an input to the `agent` node. The rest of the keys will be added to the graph state.  Warning  If you are returning `messages` in the pre-model hook, you should OVERWRITE the `messages` key by doing the following:  ``` {     "messages": [RemoveMessage(id=REMOVE_ALL_MESSAGES), *new_messages]     ... } ``` | `None` |
| `post_model_hook` | `Optional[RunnableLike]` | An optional node to add after the LLM node in the supervisor agent (i.e., the node that calls the LLM). Useful for implementing human-in-the-loop, guardrails, validation, or other post-processing. Post-model hook must be a callable or a runnable that takes in current graph state and returns a state update.  Note  Only available with `langgraph-prebuilt>=0.2.0`. | `None` |
| `parallel_tool_calls` | `bool` | Whether to allow the supervisor LLM to call tools in parallel (only OpenAI and Anthropic). Use this to control whether the supervisor can hand off to multiple agents at once. If True, will enable parallel tool calls. If False, will disable parallel tool calls (default).  Important  This is currently supported only by OpenAI and Anthropic models. To control parallel tool calling for other providers, add explicit instructions for tool use to the system prompt. | `False` |
| `state_schema` | `StateSchemaType | None` | State schema to use for the supervisor graph. | `None` |
| `config_schema` | `Type[Any] | None` | An optional schema for configuration. Use this to expose configurable parameters via `supervisor.config_specs`. | `None` |
| `output_mode` | `OutputMode` | Mode for adding managed agents' outputs to the message history in the multi-agent workflow. Can be one of:   * `full_history`: add the entire agent message history * `last_message`: add only the last message (default) | `'last_message'` |
| `add_handoff_messages` | `bool` | Whether to add a pair of (AIMessage, ToolMessage) to the message history when a handoff occurs. | `True` |
| `handoff_tool_prefix` | `Optional[str]` | Optional prefix for the handoff tools (e.g., "delegate\_to\_" or "transfer\_to\_") If provided, the handoff tools will be named `handoff_tool_prefix_agent_name`. If not provided, the handoff tools will be named `transfer_to_agent_name`. | `None` |
| `add_handoff_back_messages` | `Optional[bool]` | Whether to add a pair of (AIMessage, ToolMessage) to the message history when returning control to the supervisor to indicate that a handoff has occurred. | `None` |
| `supervisor_name` | `str` | Name of the supervisor node. | `'supervisor'` |
| `include_agent_name` | `AgentNameMode | None` | Use to specify how to expose the agent name to the underlying supervisor LLM.   * None: Relies on the LLM provider using the name attribute on the AI message. Currently, only OpenAI supports this. * `"inline"`: Add the agent name directly into the content field of the AI message using XML-style tags.   Example: `"How can I help you"` -> `"<name>agent_name</name><content>How can I help you?</content>"` | `None` |
Example
```
from langchain_openai import ChatOpenAI
from langgraph_supervisor import create_supervisor
from langgraph.prebuilt import create_react_agent
# Create specialized agents
def add(a: float, b: float) -> float:
    '''Add two numbers.'''
    return a + b
def web_search(query: str) -> str:
    '''Search the web for information.'''
    return 'Here are the headcounts for each of the FAANG companies in 2024...'
math_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[add],
    name="math_expert",
)
research_agent = create_react_agent(
    model="openai:gpt-4o",
    tools=[web_search],
    name="research_expert",
)
# Create supervisor workflow
workflow = create_supervisor(
    [research_agent, math_agent],
    model=ChatOpenAI(model="gpt-4o"),
)
# Compile and run
app = workflow.compile()
result = app.invoke({
    "messages": [
        {
            "role": "user",
            "content": "what's the combined headcount of the FAANG companies in 2024?"
        }
    ]
})
```
Functions:
| Name | Description |
| --- | --- |
| `create_handoff_tool` | Create a tool that can handoff control to the requested agent. |
| `create_forward_message_tool` | Create a tool the supervisor can use to forward a worker message by name. |
## create\_handoff\_tool [¶](#langgraph_supervisor.handoff.create_handoff_tool "Permanent link")
```
create_handoff_tool(
    *,
    agent_name: str,
    name: str | None = None,
    description: str | None = None,
    add_handoff_messages: bool = True
) -> BaseTool
```
Create a tool that can handoff control to the requested agent.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `agent_name` | `str` | The name of the agent to handoff control to, i.e. the name of the agent node in the multi-agent graph. Agent names should be simple, clear and unique, preferably in snake\_case, although you are only limited to the names accepted by LangGraph nodes as well as the tool names accepted by LLM providers (the tool name will look like this: `transfer_to_<agent_name>`). | *required* |
| `name` | `str | None` | Optional name of the tool to use for the handoff. If not provided, the tool name will be `transfer_to_<agent_name>`. | `None` |
| `description` | `str | None` | Optional description for the handoff tool. If not provided, the description will be `Ask agent <agent_name> for help`. | `None` |
| `add_handoff_messages` | `bool` | Whether to add handoff messages to the message history. If False, the handoff messages will be omitted from the message history. | `True` |
## create\_forward\_message\_tool [¶](#langgraph_supervisor.handoff.create_forward_message_tool "Permanent link")
```
create_forward_message_tool(
    supervisor_name: str = "supervisor",
) -> BaseTool
```
Create a tool the supervisor can use to forward a worker message by name.
This helps avoid information loss any time the supervisor rewrites a worker query
to the user and also can save some tokens.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `supervisor_name` | `str` | The name of the supervisor node (used for namespacing the tool). | `'supervisor'` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `BaseTool` | `BaseTool` | The 'forward\_message' tool. |
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/supervisor/)
