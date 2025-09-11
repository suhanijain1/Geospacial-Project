# Configure model

# Models[¶](#models "Permanent link")
LangGraph provides built-in support for [LLMs (language models)](https://python.langchain.com/docs/concepts/chat_models/) via the LangChain library. This makes it easy to integrate various LLMs into your agents and workflows.
## Initialize a model[¶](#initialize-a-model "Permanent link")
Use [`init_chat_model`](https://python.langchain.com/docs/how_to/chat_models_universal_init/) to initialize models:
OpenAIAnthropicAzureGoogle GeminiAWS Bedrock
```
pip install -U "langchain[openai]"
```
```
import os
from langchain.chat_models import init_chat_model
os.environ["OPENAI_API_KEY"] = "sk-..."
llm = init_chat_model("openai:gpt-4.1")
```
👉 Read the [OpenAI integration docs](https://python.langchain.com/docs/integrations/chat/openai/)
```
pip install -U "langchain[anthropic]"
```
```
import os
from langchain.chat_models import init_chat_model
os.environ["ANTHROPIC_API_KEY"] = "sk-..."
llm = init_chat_model("anthropic:claude-3-5-sonnet-latest")
```
👉 Read the [Anthropic integration docs](https://python.langchain.com/docs/integrations/chat/anthropic/)
```
pip install -U "langchain[openai]"
```
```
import os
from langchain.chat_models import init_chat_model
os.environ["AZURE_OPENAI_API_KEY"] = "..."
os.environ["AZURE_OPENAI_ENDPOINT"] = "..."
os.environ["OPENAI_API_VERSION"] = "2025-03-01-preview"
llm = init_chat_model(
    "azure_openai:gpt-4.1",
    azure_deployment=os.environ["AZURE_OPENAI_DEPLOYMENT_NAME"],
)
```
👉 Read the [Azure integration docs](https://python.langchain.com/docs/integrations/chat/azure_chat_openai/)
```
pip install -U "langchain[google-genai]"
```
```
import os
from langchain.chat_models import init_chat_model
os.environ["GOOGLE_API_KEY"] = "..."
llm = init_chat_model("google_genai:gemini-2.0-flash")
```
👉 Read the [Google GenAI integration docs](https://python.langchain.com/docs/integrations/chat/google_generative_ai/)
```
pip install -U "langchain[aws]"
```
```
from langchain.chat_models import init_chat_model
# Follow the steps here to configure your credentials:
# https://docs.aws.amazon.com/bedrock/latest/userguide/getting-started.html
llm = init_chat_model(
    "anthropic.claude-3-5-sonnet-20240620-v1:0",
    model_provider="bedrock_converse",
)
```
👉 Read the [AWS Bedrock integration docs](https://python.langchain.com/docs/integrations/chat/bedrock/)
### Instantiate a model directly[¶](#instantiate-a-model-directly "Permanent link")
If a model provider is not available via `init_chat_model`, you can instantiate the provider's model class directly. The model must implement the [BaseChatModel interface](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.chat_models.BaseChatModel.html) and support tool calling:
*API Reference: [ChatAnthropic](https://python.langchain.com/api_reference/anthropic/chat_models/langchain_anthropic.chat_models.ChatAnthropic.html)*
```
# Anthropic is already supported by `init_chat_model`,
# but you can also instantiate it directly.
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(
  model="claude-3-7-sonnet-latest",
  temperature=0,
  max_tokens=2048
)
```
Tool calling support
If you are building an agent or workflow that requires the model to call external tools, ensure that the underlying
language model supports [tool calling](../../concepts/tools/). Compatible models can be found in the [LangChain integrations directory](https://python.langchain.com/docs/integrations/chat/).
## Use in an agent[¶](#use-in-an-agent "Permanent link")
When using `create_react_agent` you can specify the model by its name string, which is a shorthand for initializing the model using `init_chat_model`. This allows you to use the model without needing to import or instantiate it directly.
model namemodel instance
```
from langgraph.prebuilt import create_react_agent
create_react_agent(
   model="anthropic:claude-3-7-sonnet-latest",
   # other parameters
)
```
```
from langchain_anthropic import ChatAnthropic
from langgraph.prebuilt import create_react_agent
model = ChatAnthropic(
    model="claude-3-7-sonnet-latest",
    temperature=0,
    max_tokens=2048
)
# Alternatively
# model = init_chat_model("anthropic:claude-3-7-sonnet-latest")
agent = create_react_agent(
  model=model,
  # other parameters
)
```
### Dynamic model selection[¶](#dynamic-model-selection "Permanent link")
Pass a callable function to `create_react_agent` to dynamically select the model at runtime. This is useful for scenarios where you want to choose a model based on user input, configuration settings, or other runtime conditions.
The selector function must return a chat model. If you're using tools, you must bind the tools to the model within the selector function.
*API Reference: [init\_chat\_model](https://python.langchain.com/api_reference/langchain/chat_models/langchain.chat_models.base.init_chat_model.html) | [BaseChatModel](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.chat_models.BaseChatModel.html) | [tool](https://python.langchain.com/api_reference/core/tools/langchain_core.tools.convert.tool.html) | [create\_react\_agent](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.create_react_agent) | [AgentState](https://langchain-ai.github.io/langgraph/reference/prebuilt/#langgraph.prebuilt.chat_agent_executor.AgentState)*
```
from dataclasses import dataclass
from typing import Literal
from langchain.chat_models import init_chat_model
from langchain_core.language_models import BaseChatModel
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langgraph.prebuilt.chat_agent_executor import AgentState
from langgraph.runtime import Runtime
@tool
def weather() -> str:
    """Returns the current weather conditions."""
    return "It's nice and sunny."
# Define the runtime context
@dataclass
class CustomContext:
    provider: Literal["anthropic", "openai"]
# Initialize models
openai_model = init_chat_model("openai:gpt-4o")
anthropic_model = init_chat_model("anthropic:claude-sonnet-4-20250514")
# Selector function for model choice
def select_model(state: AgentState, runtime: Runtime[CustomContext]) -> BaseChatModel:
    if runtime.context.provider == "anthropic":
        model = anthropic_model
    elif runtime.context.provider == "openai":
        model = openai_model
    else:
        raise ValueError(f"Unsupported provider: {runtime.context.provider}")
    # With dynamic model selection, you must bind tools explicitly
    return model.bind_tools([weather])
# Create agent with dynamic model selection
agent = create_react_agent(select_model, tools=[weather])
# Invoke with context to select model
output = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Which model is handling this?",
            }
        ]
    },
    context=CustomContext(provider="openai"),
)
print(output["messages"][-1].text())
```
New in LangGraph v0.6
## Advanced model configuration[¶](#advanced-model-configuration "Permanent link")
### Disable streaming[¶](#disable-streaming "Permanent link")
To disable streaming of the individual LLM tokens, set `disable_streaming=True` when initializing the model:
`init_chat_model``ChatModel`
```
from langchain.chat_models import init_chat_model
model = init_chat_model(
    "anthropic:claude-3-7-sonnet-latest",
    disable_streaming=True
)
```
```
from langchain_anthropic import ChatAnthropic
model = ChatAnthropic(
    model="claude-3-7-sonnet-latest",
    disable_streaming=True
)
```
Refer to the [API reference](https://python.langchain.com/api_reference/core/language_models/langchain_core.language_models.chat_models.BaseChatModel.html#langchain_core.language_models.chat_models.BaseChatModel.disable_streaming) for more information on `disable_streaming`
### Add model fallbacks[¶](#add-model-fallbacks "Permanent link")
You can add a fallback to a different model or a different LLM provider using `model.with_fallbacks([...])`:
`init_chat_model``ChatModel`
```
from langchain.chat_models import init_chat_model
model_with_fallbacks = (
    init_chat_model("anthropic:claude-3-5-haiku-latest")
    .with_fallbacks([
        init_chat_model("openai:gpt-4.1-mini"),
    ])
)
```
```
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
model_with_fallbacks = (
    ChatAnthropic(model="claude-3-5-haiku-latest")
    .with_fallbacks([
        ChatOpenAI(model="gpt-4.1-mini"),
    ])
)
```
See this [guide](https://python.langchain.com/docs/how_to/fallbacks/#fallback-to-better-model) for more information on model fallbacks.
### Use the built-in rate limiter[¶](#use-the-built-in-rate-limiter "Permanent link")
Langchain includes a built-in in-memory rate limiter. This rate limiter is thread safe and can be shared by multiple threads in the same process.
*API Reference: [InMemoryRateLimiter](https://python.langchain.com/api_reference/core/rate_limiters/langchain_core.rate_limiters.InMemoryRateLimiter.html) | [ChatAnthropic](https://python.langchain.com/api_reference/anthropic/chat_models/langchain_anthropic.chat_models.ChatAnthropic.html)*
```
from langchain_core.rate_limiters import InMemoryRateLimiter
from langchain_anthropic import ChatAnthropic
rate_limiter = InMemoryRateLimiter(
    requests_per_second=0.1,  # <-- Super slow! We can only make a request once every 10 seconds!!
    check_every_n_seconds=0.1,  # Wake up every 100 ms to check whether allowed to make a request,
    max_bucket_size=10,  # Controls the maximum burst size.
)
model = ChatAnthropic(
   model_name="claude-3-opus-20240229",
   rate_limiter=rate_limiter
)
```
See the LangChain docs for more information on how to [handle rate limiting](https://python.langchain.com/docs/how_to/chat_model_rate_limiting/).
## Bring your own model[¶](#bring-your-own-model "Permanent link")
If your desired LLM isn't officially supported by LangChain, consider these options:
1. **Implement a custom LangChain chat model**: Create a model conforming to the [LangChain chat model interface](https://python.langchain.com/docs/how_to/custom_chat_model/). This enables full compatibility with LangGraph's agents and workflows but requires understanding of the LangChain framework.
2. **Direct invocation with custom streaming**: Use your model directly by [adding custom streaming logic](../../how-tos/streaming/#use-with-any-llm) with `StreamWriter`.
   Refer to the [custom streaming documentation](../../how-tos/streaming/#use-with-any-llm) for guidance. This approach suits custom workflows where prebuilt agent integration is not necessary.
## Additional resources[¶](#additional-resources "Permanent link")
* [Multimodal inputs](https://python.langchain.com/docs/how_to/multimodal_inputs/)
* [Structured outputs](https://python.langchain.com/docs/how_to/structured_output/)
* [Model integration directory](https://python.langchain.com/docs/integrations/chat/)
* [Force model to call a specific tool](https://python.langchain.com/docs/how_to/tool_choice/)
* [All chat model how-to guides](https://python.langchain.com/docs/how_to/#chat-models)
* [Chat model integrations](https://python.langchain.com/docs/integrations/chat/)
Back to top

[Source](https://langchain-ai.github.io/langgraph/agents/models/)
