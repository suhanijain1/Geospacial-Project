# Errors

# Errors[¶](#errors "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `EmptyChannelError` | Raised when attempting to get the value of a channel that hasn't been updated |
| `GraphRecursionError` | Raised when the graph has exhausted the maximum number of steps. |
| `InvalidUpdateError` | Raised when attempting to update a channel with an invalid set of updates. |
| `GraphInterrupt` | Raised when a subgraph is interrupted, suppressed by the root graph. |
| `NodeInterrupt` | Raised by a node to interrupt execution. |
| `EmptyInputError` | Raised when graph receives an empty input. |
| `TaskNotFound` | Raised when the executor is unable to find a task (for distributed mode). |
## EmptyChannelError [¶](#langgraph.errors.EmptyChannelError "Permanent link")
Bases: `Exception`
Raised when attempting to get the value of a channel that hasn't been updated
for the first time yet.
## GraphRecursionError [¶](#langgraph.errors.GraphRecursionError "Permanent link")
Bases: `RecursionError`
Raised when the graph has exhausted the maximum number of steps.
This prevents infinite loops. To increase the maximum number of steps,
run your graph with a config specifying a higher `recursion_limit`.
Troubleshooting Guides:
* [GRAPH\_RECURSION\_LIMIT](https://python.langchain.com/docs/troubleshooting/errors/GRAPH_RECURSION_LIMIT)
Examples:
```
graph = builder.compile()
graph.invoke(
    {"messages": [("user", "Hello, world!")]},
    # The config is the second positional argument
    {"recursion_limit": 1000},
)
```
## InvalidUpdateError [¶](#langgraph.errors.InvalidUpdateError "Permanent link")
Bases: `Exception`
Raised when attempting to update a channel with an invalid set of updates.
Troubleshooting Guides:
* [INVALID\_CONCURRENT\_GRAPH\_UPDATE](https://python.langchain.com/docs/troubleshooting/errors/INVALID_CONCURRENT_GRAPH_UPDATE)
* [INVALID\_GRAPH\_NODE\_RETURN\_VALUE](https://python.langchain.com/docs/troubleshooting/errors/INVALID_GRAPH_NODE_RETURN_VALUE)
## GraphInterrupt [¶](#langgraph.errors.GraphInterrupt "Permanent link")
Bases: `GraphBubbleUp`
Raised when a subgraph is interrupted, suppressed by the root graph.
Never raised directly, or surfaced to the user.
## NodeInterrupt [¶](#langgraph.errors.NodeInterrupt "Permanent link")
Bases: `GraphInterrupt`
Raised by a node to interrupt execution.
Deprecated in V1.0.0 in favor of [`interrupt`](../types/#langgraph.types.interrupt "<code class=\"doc-symbol doc-symbol-heading doc-symbol-function\"></code>            <span class=\"doc doc-object-name doc-function-name\">interrupt</span>").
## EmptyInputError [¶](#langgraph.errors.EmptyInputError "Permanent link")
Bases: `Exception`
Raised when graph receives an empty input.
## TaskNotFound [¶](#langgraph.errors.TaskNotFound "Permanent link")
Bases: `Exception`
Raised when the executor is unable to find a task (for distributed mode).
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/errors/)
