# Use MCP

# Use MCP[¶](#use-mcp "Permanent link")
[Model Context Protocol (MCP)](https://modelcontextprotocol.io/introduction) is an open protocol that standardizes how applications provide tools and context to language models. LangGraph agents can use tools defined on MCP servers through the `langchain-mcp-adapters` library.
![MCP](../assets/mcp.png)
Install the `langchain-mcp-adapters` library to use MCP tools in LangGraph:
```
pip install langchain-mcp-adapters
```
## Use MCP tools[¶](#use-mcp-tools "Permanent link")
The `langchain-mcp-adapters` package enables agents to use tools defined across one or more MCP servers.
In an agentIn a workflow
Agent using tools defined on MCP servers
```
from langchain_mcp_adapters.client import MultiServerMCPClient
from langgraph.prebuilt import create_react_agent
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Replace with absolute path to your math_server.py file
            "args": ["/path/to/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # Ensure you start your weather server on port 8000
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    }
)
tools = await client.get_tools()
agent = create_react_agent(
    "anthropic:claude-3-7-sonnet-latest",
    tools
)
math_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
weather_response = await agent.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)
```
Workflow using MCP tools with ToolNode
```
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain.chat_models import init_chat_model
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode
# Initialize the model
model = init_chat_model("anthropic:claude-3-5-sonnet-latest")
# Set up MCP client
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["./examples/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # make sure you start your weather server on port 8000
            "url": "http://localhost:8000/mcp/",
            "transport": "streamable_http",
        }
    }
)
tools = await client.get_tools()
# Bind tools to model
model_with_tools = model.bind_tools(tools)
# Create ToolNode
tool_node = ToolNode(tools)
def should_continue(state: MessagesState):
    messages = state["messages"]
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    return END
# Define call_model function
async def call_model(state: MessagesState):
    messages = state["messages"]
    response = await model_with_tools.ainvoke(messages)
    return {"messages": [response]}
# Build the graph
builder = StateGraph(MessagesState)
builder.add_node("call_model", call_model)
builder.add_node("tools", tool_node)
builder.add_edge(START, "call_model")
builder.add_conditional_edges(
    "call_model",
    should_continue,
)
builder.add_edge("tools", "call_model")
# Compile the graph
graph = builder.compile()
# Test the graph
math_response = await graph.ainvoke(
    {"messages": [{"role": "user", "content": "what's (3 + 5) x 12?"}]}
)
weather_response = await graph.ainvoke(
    {"messages": [{"role": "user", "content": "what is the weather in nyc?"}]}
)
```
## Custom MCP servers[¶](#custom-mcp-servers "Permanent link")
To create your own MCP servers, you can use the `mcp` library. This library provides a simple way to define tools and run them as servers.
Install the MCP library:
```
pip install mcp
```
Use the following reference implementations to test your agent with MCP tool servers.
Example Math Server (stdio transport)
```
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Math")
@mcp.tool()
def add(a: int, b: int) -> int:
    """Add two numbers"""
    return a + b
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """Multiply two numbers"""
    return a * b
if __name__ == "__main__":
    mcp.run(transport="stdio")
```
Example Weather Server (Streamable HTTP transport)
```
from mcp.server.fastmcp import FastMCP
mcp = FastMCP("Weather")
@mcp.tool()
async def get_weather(location: str) -> str:
    """Get weather for location."""
    return "It's always sunny in New York"
if __name__ == "__main__":
    mcp.run(transport="streamable-http")
```
## Additional resources[¶](#additional-resources "Permanent link")
* [MCP documentation](https://modelcontextprotocol.io/introduction)
* [MCP Transport documentation](https://modelcontextprotocol.io/docs/concepts/transports)
* [langchain\_mcp\_adapters](https://github.com/langchain-ai/langchain-mcp-adapters)
Back to top

[Source](https://langchain-ai.github.io/langgraph/agents/mcp/)
