# MCP Adapters

# LangChain Model Context Protocol (MCP) Adapters[¶](#langchain-model-context-protocol-mcp-adapters "Permanent link")
Client for connecting to multiple MCP servers and loading LangChain-compatible resources.
This module provides the MultiServerMCPClient class for managing connections to multiple
MCP servers and loading tools, prompts, and resources from them.
Classes:
| Name | Description |
| --- | --- |
| `MultiServerMCPClient` | Client for connecting to multiple MCP servers and loading LangChain-compatible tools, prompts and resources from them. |
## MultiServerMCPClient [¶](#langchain_mcp_adapters.client.MultiServerMCPClient "Permanent link")
Client for connecting to multiple MCP servers and loading LangChain-compatible tools, prompts and resources from them.
Methods:
| Name | Description |
| --- | --- |
| `__init__` | Initialize a MultiServerMCPClient with MCP servers connections. |
| `session` | Connect to an MCP server and initialize a session. |
| `get_tools` | Get a list of all tools from all connected servers. |
| `get_prompt` | Get a prompt from a given MCP server. |
| `get_resources` | Get resources from a given MCP server. |
| `__aenter__` | Async context manager entry point. |
| `__aexit__` | Async context manager exit point. |
### \_\_init\_\_ [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.__init__ "Permanent link")
```
__init__(
    connections: dict[str, Connection] | None = None,
) -> None
```
Initialize a MultiServerMCPClient with MCP servers connections.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `connections` | `dict[str, Connection] | None` | A dictionary mapping server names to connection configurations. If None, no initial connections are established. | `None` |
Example: basic usage (starting a new session on each tool call)
```
from langchain_mcp_adapters.client import MultiServerMCPClient
client = MultiServerMCPClient(
    {
        "math": {
            "command": "python",
            # Make sure to update to the full absolute path to your math_server.py file
            "args": ["/path/to/math_server.py"],
            "transport": "stdio",
        },
        "weather": {
            # Make sure you start your weather server on port 8000
            "url": "http://localhost:8000/mcp",
            "transport": "streamable_http",
        }
    }
)
all_tools = await client.get_tools()
```
Example: explicitly starting a session
```
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
client = MultiServerMCPClient({...})
async with client.session("math") as session:
    tools = await load_mcp_tools(session)
```
### session `async` [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.session "Permanent link")
```
session(
    server_name: str, *, auto_initialize: bool = True
) -> AsyncIterator[ClientSession]
```
Connect to an MCP server and initialize a session.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `server_name` | `str` | Name to identify this server connection | *required* |
| `auto_initialize` | `bool` | Whether to automatically initialize the session | `True` |
Raises:
| Type | Description |
| --- | --- |
| `ValueError` | If the server name is not found in the connections |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[ClientSession]` | An initialized ClientSession |
### get\_tools `async` [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.get_tools "Permanent link")
```
get_tools(
    *, server_name: str | None = None
) -> list[BaseTool]
```
Get a list of all tools from all connected servers.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `server_name` | `str | None` | Optional name of the server to get tools from. If None, all tools from all servers will be returned (default). | `None` |
NOTE: a new session will be created for each tool call
Returns:
| Type | Description |
| --- | --- |
| `list[BaseTool]` | A list of LangChain tools |
### get\_prompt `async` [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.get_prompt "Permanent link")
```
get_prompt(
    server_name: str,
    prompt_name: str,
    *,
    arguments: dict[str, Any] | None = None
) -> list[HumanMessage | AIMessage]
```
Get a prompt from a given MCP server.
### get\_resources `async` [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.get_resources "Permanent link")
```
get_resources(
    server_name: str, *, uris: str | list[str] | None = None
) -> list[Blob]
```
Get resources from a given MCP server.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `server_name` | `str` | Name of the server to get resources from | *required* |
| `uris` | `str | list[str] | None` | Optional resource URI or list of URIs to load. If not provided, all resources will be loaded. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[Blob]` | A list of LangChain Blobs |
### \_\_aenter\_\_ `async` [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.__aenter__ "Permanent link")
```
__aenter__() -> MultiServerMCPClient
```
Async context manager entry point.
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Context manager support has been removed. |
### \_\_aexit\_\_ [¶](#langchain_mcp_adapters.client.MultiServerMCPClient.__aexit__ "Permanent link")
```
__aexit__(
    exc_type: type[BaseException] | None,
    exc_val: BaseException | None,
    exc_tb: TracebackType | None,
) -> None
```
Async context manager exit point.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `exc_type` | `type[BaseException] | None` | Exception type if an exception occurred. | *required* |
| `exc_val` | `BaseException | None` | Exception value if an exception occurred. | *required* |
| `exc_tb` | `TracebackType | None` | Exception traceback if an exception occurred. | *required* |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Context manager support has been removed. |
Tools adapter for converting MCP tools to LangChain tools.
This module provides functionality to convert MCP tools into LangChain-compatible
tools, handle tool execution, and manage tool conversion between the two formats.
Functions:
| Name | Description |
| --- | --- |
| `load_mcp_tools` | Load all available MCP tools and convert them to LangChain tools. |
## load\_mcp\_tools `async` [¶](#langchain_mcp_adapters.tools.load_mcp_tools "Permanent link")
```
load_mcp_tools(
    session: ClientSession | None,
    *,
    connection: Connection | None = None
) -> list[BaseTool]
```
Load all available MCP tools and convert them to LangChain tools.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `session` | `ClientSession | None` | The MCP client session. If None, connection must be provided. | *required* |
| `connection` | `Connection | None` | Connection config to create a new session if session is None. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[BaseTool]` | List of LangChain tools. Tool annotations are returned as part |
| `list[BaseTool]` | of the tool metadata object. |
Raises:
| Type | Description |
| --- | --- |
| `ValueError` | If neither session nor connection is provided. |
Prompts adapter for converting MCP prompts to LangChain messages.
This module provides functionality to convert MCP prompt messages into LangChain
message objects, handling both user and assistant message types.
Functions:
| Name | Description |
| --- | --- |
| `load_mcp_prompt` | Load MCP prompt and convert to LangChain messages. |
## load\_mcp\_prompt `async` [¶](#langchain_mcp_adapters.prompts.load_mcp_prompt "Permanent link")
```
load_mcp_prompt(
    session: ClientSession,
    name: str,
    *,
    arguments: dict[str, Any] | None = None
) -> list[HumanMessage | AIMessage]
```
Load MCP prompt and convert to LangChain messages.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `session` | `ClientSession` | The MCP client session. | *required* |
| `name` | `str` | Name of the prompt to load. | *required* |
| `arguments` | `dict[str, Any] | None` | Optional arguments to pass to the prompt. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[HumanMessage | AIMessage]` | A list of LangChain messages converted from the MCP prompt. |
Resources adapter for converting MCP resources to LangChain Blobs.
This module provides functionality to convert MCP resources into LangChain Blob
objects, handling both text and binary resource content types.
Functions:
| Name | Description |
| --- | --- |
| `load_mcp_resources` | Load MCP resources and convert them to LangChain Blobs. |
## load\_mcp\_resources `async` [¶](#langchain_mcp_adapters.resources.load_mcp_resources "Permanent link")
```
load_mcp_resources(
    session: ClientSession,
    *,
    uris: str | list[str] | None = None
) -> list[Blob]
```
Load MCP resources and convert them to LangChain Blobs.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `session` | `ClientSession` | MCP client session. | *required* |
| `uris` | `str | list[str] | None` | List of URIs to load. If None, all resources will be loaded. Note: Dynamic resources will NOT be loaded when None is specified, as they require parameters and are ignored by the MCP SDK's session.list\_resources() method. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[Blob]` | A list of LangChain Blobs. |
Raises:
| Type | Description |
| --- | --- |
| `RuntimeError` | If an error occurs while fetching a resource. |
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/mcp/)
