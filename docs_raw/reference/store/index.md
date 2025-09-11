# Storage

# Storage[¶](#storage "Permanent link")
Base classes and types for persistent key-value stores.
Stores provide long-term memory that persists across threads and conversations.
Supports hierarchical namespaces, key-value storage, and optional vector search.
Core types
* BaseStore: Store interface with sync/async operations
* Item: Stored key-value pairs with metadata
* Op: Get/Put/Search/List operations
Modules:
| Name | Description |
| --- | --- |
| `batch` | Utilities for batching operations in a background task. |
| `embed` | Utilities for working with embedding functions and LangChain's Embeddings interface. |
Classes:
| Name | Description |
| --- | --- |
| `Embeddings` | Interface for embedding models. |
| `Item` | Represents a stored item with metadata. |
| `GetOp` | Operation to retrieve a specific item by its namespace and key. |
| `SearchOp` | Operation to search for items within a specified namespace hierarchy. |
| `MatchCondition` | Represents a pattern for matching namespaces in the store. |
| `ListNamespacesOp` | Operation to list and filter namespaces in the store. |
| `PutOp` | Operation to store, update, or delete an item in the store. |
| `BaseStore` | Abstract base class for persistent key-value stores. |
Functions:
| Name | Description |
| --- | --- |
| `ensure_embeddings` | Ensure that an embedding function conforms to LangChain's Embeddings interface. |
| `get_text_at_path` | Extract text from an object using a path expression or pre-tokenized path. |
| `tokenize_path` | Tokenize a path into components. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `NamespacePath` |  | A tuple representing a namespace path that can include wildcards. |
| `NamespaceMatchType` |  | Specifies how to match namespace paths. |
## NamespacePath `module-attribute` [¶](#langgraph.store.base.NamespacePath "Permanent link")
```
NamespacePath = tuple[Union[str, Literal['*']], ...]
```
A tuple representing a namespace path that can include wildcards.
Examples
```
("users",)  # Exact users namespace
("documents", "*")  # Any sub-namespace under documents
("cache", "*", "v1")  # Any cache category with v1 version
```
## NamespaceMatchType `module-attribute` [¶](#langgraph.store.base.NamespaceMatchType "Permanent link")
```
NamespaceMatchType = Literal['prefix', 'suffix']
```
Specifies how to match namespace paths.
Values
"prefix": Match from the start of the namespace
"suffix": Match from the end of the namespace
## Embeddings [¶](#langgraph.store.base.Embeddings "Permanent link")
Bases: `ABC`
Interface for embedding models.
This is an interface meant for implementing text embedding models.
Text embedding models are used to map text to a vector (a point in n-dimensional
space).
Texts that are similar will usually be mapped to points that are close to each
other in this space. The exact details of what's considered "similar" and how
"distance" is measured in this space are dependent on the specific embedding model.
This abstraction contains a method for embedding a list of documents and a method
for embedding a query text. The embedding of a query text is expected to be a single
vector, while the embedding of a list of documents is expected to be a list of
vectors.
Usually the query embedding is identical to the document embedding, but the
abstraction allows treating them independently.
In addition to the synchronous methods, this interface also provides asynchronous
versions of the methods.
By default, the asynchronous methods are implemented using the synchronous methods;
however, implementations may choose to override the asynchronous methods with
an async native implementation for performance reasons.
Methods:
| Name | Description |
| --- | --- |
| `embed_documents` | Embed search docs. |
| `embed_query` | Embed query text. |
| `aembed_documents` | Asynchronous Embed search docs. |
| `aembed_query` | Asynchronous Embed query text. |
### embed\_documents `abstractmethod` [¶](#langgraph.store.base.Embeddings.embed_documents "Permanent link")
```
embed_documents(texts: list[str]) -> list[list[float]]
```
Embed search docs.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `texts` | `list[str]` | List of text to embed. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `list[list[float]]` | List of embeddings. |
### embed\_query `abstractmethod` [¶](#langgraph.store.base.Embeddings.embed_query "Permanent link")
```
embed_query(text: str) -> list[float]
```
Embed query text.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `text` | `str` | Text to embed. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `list[float]` | Embedding. |
### aembed\_documents `async` [¶](#langgraph.store.base.Embeddings.aembed_documents "Permanent link")
```
aembed_documents(texts: list[str]) -> list[list[float]]
```
Asynchronous Embed search docs.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `texts` | `list[str]` | List of text to embed. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `list[list[float]]` | List of embeddings. |
### aembed\_query `async` [¶](#langgraph.store.base.Embeddings.aembed_query "Permanent link")
```
aembed_query(text: str) -> list[float]
```
Asynchronous Embed query text.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `text` | `str` | Text to embed. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `list[float]` | Embedding. |
## NotProvided [¶](#langgraph.store.base.NotProvided "Permanent link")
Sentinel singleton.
## Item [¶](#langgraph.store.base.Item "Permanent link")
Represents a stored item with metadata.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `value` | `dict[str, Any]` | The stored data as a dictionary. Keys are filterable. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
| `namespace` | `tuple[str, ...]` | Hierarchical path defining the collection in which this document resides. Represented as a tuple of strings, allowing for nested categorization. For example: ("documents", 'user123') | *required* |
| `created_at` | `datetime` | Timestamp of item creation. | *required* |
| `updated_at` | `datetime` | Timestamp of last update. | *required* |
## SearchItem [¶](#langgraph.store.base.SearchItem "Permanent link")
Bases: `Item`
Represents an item returned from a search operation with additional metadata.
Methods:
| Name | Description |
| --- | --- |
| `__init__` | Initialize a result item. |
### \_\_init\_\_ [¶](#langgraph.store.base.SearchItem.__init__ "Permanent link")
```
__init__(
    namespace: tuple[str, ...],
    key: str,
    value: dict[str, Any],
    created_at: datetime,
    updated_at: datetime,
    score: float | None = None,
) -> None
```
Initialize a result item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path to the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
| `value` | `dict[str, Any]` | The stored value. | *required* |
| `created_at` | `datetime` | When the item was first created. | *required* |
| `updated_at` | `datetime` | When the item was last updated. | *required* |
| `score` | `float | None` | Relevance/similarity score if from a ranked operation. | `None` |
## GetOp [¶](#langgraph.store.base.GetOp "Permanent link")
Bases: `NamedTuple`
Operation to retrieve a specific item by its namespace and key.
This operation allows precise retrieval of stored items using their full path
(namespace) and unique identifier (key) combination.
Examples
Basic item retrieval:
```
GetOp(namespace=("users", "profiles"), key="user123")
GetOp(namespace=("cache", "embeddings"), key="doc456")
```
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path that uniquely identifies the item's location. |
| `key` | `str` | Unique identifier for the item within its specific namespace. |
| `refresh_ttl` | `bool` | Whether to refresh TTLs for the returned item. |
### namespace `instance-attribute` [¶](#langgraph.store.base.GetOp.namespace "Permanent link")
```
namespace: tuple[str, ...]
```
Hierarchical path that uniquely identifies the item's location.
Examples
```
("users",)  # Root level users namespace
("users", "profiles")  # Profiles within users namespace
```
### key `instance-attribute` [¶](#langgraph.store.base.GetOp.key "Permanent link")
```
key: str
```
Unique identifier for the item within its specific namespace.
Examples
```
"user123"  # For a user profile
"doc456"  # For a document
```
### refresh\_ttl `class-attribute` `instance-attribute` [¶](#langgraph.store.base.GetOp.refresh_ttl "Permanent link")
```
refresh_ttl: bool = True
```
Whether to refresh TTLs for the returned item.
If no TTL was specified for the original item(s),
or if TTL support is not enabled for your adapter,
this argument is ignored.
## SearchOp [¶](#langgraph.store.base.SearchOp "Permanent link")
Bases: `NamedTuple`
Operation to search for items within a specified namespace hierarchy.
This operation supports both structured filtering and natural language search
within a given namespace prefix. It provides pagination through limit and offset
parameters.
Note
Natural language search support depends on your store implementation.
Examples
Search with filters and pagination:
```
SearchOp(
    namespace_prefix=("documents",),
    filter={"type": "report", "status": "active"},
    limit=5,
    offset=10
)
```
Natural language search:
```
SearchOp(
    namespace_prefix=("users", "content"),
    query="technical documentation about APIs",
    limit=20
)
```
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `namespace_prefix` | `tuple[str, ...]` | Hierarchical path prefix defining the search scope. |
| `filter` | `dict[str, Any] | None` | Key-value pairs for filtering results based on exact matches or comparison operators. |
| `limit` | `int` | Maximum number of items to return in the search results. |
| `offset` | `int` | Number of matching items to skip for pagination. |
| `query` | `str | None` | Natural language search query for semantic search capabilities. |
| `refresh_ttl` | `bool` | Whether to refresh TTLs for the returned item. |
### namespace\_prefix `instance-attribute` [¶](#langgraph.store.base.SearchOp.namespace_prefix "Permanent link")
```
namespace_prefix: tuple[str, ...]
```
Hierarchical path prefix defining the search scope.
Examples
```
()  # Search entire store
("documents",)  # Search all documents
("users", "content")  # Search within user content
```
### filter `class-attribute` `instance-attribute` [¶](#langgraph.store.base.SearchOp.filter "Permanent link")
```
filter: dict[str, Any] | None = None
```
Key-value pairs for filtering results based on exact matches or comparison operators.
The filter supports both exact matches and operator-based comparisons.
Supported Operators
* $eq: Equal to (same as direct value comparison)
* $ne: Not equal to
* $gt: Greater than
* $gte: Greater than or equal to
* $lt: Less than
* $lte: Less than or equal to
Examples
Simple exact match:
```
{"status": "active"}
```
Comparison operators:
```
{"score": {"$gt": 4.99}}  # Score greater than 4.99
```
Multiple conditions:
```
{
    "score": {"$gte": 3.0},
    "color": "red"
}
```
### limit `class-attribute` `instance-attribute` [¶](#langgraph.store.base.SearchOp.limit "Permanent link")
```
limit: int = 10
```
Maximum number of items to return in the search results.
### offset `class-attribute` `instance-attribute` [¶](#langgraph.store.base.SearchOp.offset "Permanent link")
```
offset: int = 0
```
Number of matching items to skip for pagination.
### query `class-attribute` `instance-attribute` [¶](#langgraph.store.base.SearchOp.query "Permanent link")
```
query: str | None = None
```
Natural language search query for semantic search capabilities.
Examples
* "technical documentation about REST APIs"
* "machine learning papers from 2023"
### refresh\_ttl `class-attribute` `instance-attribute` [¶](#langgraph.store.base.SearchOp.refresh_ttl "Permanent link")
```
refresh_ttl: bool = True
```
Whether to refresh TTLs for the returned item.
If no TTL was specified for the original item(s),
or if TTL support is not enabled for your adapter,
this argument is ignored.
## MatchCondition [¶](#langgraph.store.base.MatchCondition "Permanent link")
Bases: `NamedTuple`
Represents a pattern for matching namespaces in the store.
This class combines a match type (prefix or suffix) with a namespace path
pattern that can include wildcards to flexibly match different namespace
hierarchies.
Examples
Prefix matching:
```
MatchCondition(match_type="prefix", path=("users", "profiles"))
```
Suffix matching with wildcard:
```
MatchCondition(match_type="suffix", path=("cache", "*"))
```
Simple suffix matching:
```
MatchCondition(match_type="suffix", path=("v1",))
```
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `match_type` | `NamespaceMatchType` | Type of namespace matching to perform. |
| `path` | `NamespacePath` | Namespace path pattern that can include wildcards. |
### match\_type `instance-attribute` [¶](#langgraph.store.base.MatchCondition.match_type "Permanent link")
```
match_type: NamespaceMatchType
```
Type of namespace matching to perform.
### path `instance-attribute` [¶](#langgraph.store.base.MatchCondition.path "Permanent link")
```
path: NamespacePath
```
Namespace path pattern that can include wildcards.
## ListNamespacesOp [¶](#langgraph.store.base.ListNamespacesOp "Permanent link")
Bases: `NamedTuple`
Operation to list and filter namespaces in the store.
This operation allows exploring the organization of data, finding specific
collections, and navigating the namespace hierarchy.
Examples
List all namespaces under the "documents" path:
```
ListNamespacesOp(
    match_conditions=(MatchCondition(match_type="prefix", path=("documents",)),),
    max_depth=2
)
```
List all namespaces that end with "v1":
```
ListNamespacesOp(
    match_conditions=(MatchCondition(match_type="suffix", path=("v1",)),),
    limit=50
)
```
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `match_conditions` | `tuple[MatchCondition, ...] | None` | Optional conditions for filtering namespaces. |
| `max_depth` | `int | None` | Maximum depth of namespace hierarchy to return. |
| `limit` | `int` | Maximum number of namespaces to return. |
| `offset` | `int` | Number of namespaces to skip for pagination. |
### match\_conditions `class-attribute` `instance-attribute` [¶](#langgraph.store.base.ListNamespacesOp.match_conditions "Permanent link")
```
match_conditions: tuple[MatchCondition, ...] | None = None
```
Optional conditions for filtering namespaces.
Examples
All user namespaces:
```
(MatchCondition(match_type="prefix", path=("users",)),)
```
All namespaces that start with "docs" and end with "draft":
```
(
    MatchCondition(match_type="prefix", path=("docs",)),
    MatchCondition(match_type="suffix", path=("draft",))
)
```
### max\_depth `class-attribute` `instance-attribute` [¶](#langgraph.store.base.ListNamespacesOp.max_depth "Permanent link")
```
max_depth: int | None = None
```
Maximum depth of namespace hierarchy to return.
Note
Namespaces deeper than this level will be truncated.
### limit `class-attribute` `instance-attribute` [¶](#langgraph.store.base.ListNamespacesOp.limit "Permanent link")
```
limit: int = 100
```
Maximum number of namespaces to return.
### offset `class-attribute` `instance-attribute` [¶](#langgraph.store.base.ListNamespacesOp.offset "Permanent link")
```
offset: int = 0
```
Number of namespaces to skip for pagination.
## PutOp [¶](#langgraph.store.base.PutOp "Permanent link")
Bases: `NamedTuple`
Operation to store, update, or delete an item in the store.
This class represents a single operation to modify the store's contents,
whether adding new items, updating existing ones, or removing them.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path that identifies the location of the item. |
| `key` | `str` | Unique identifier for the item within its namespace. |
| `value` | `dict[str, Any] | None` | The data to store, or None to mark the item for deletion. |
| `index` | `Literal[False] | list[str] | None` | Controls how the item's fields are indexed for search operations. |
| `ttl` | `float | None` | Controls the TTL (time-to-live) for the item in minutes. |
### namespace `instance-attribute` [¶](#langgraph.store.base.PutOp.namespace "Permanent link")
```
namespace: tuple[str, ...]
```
Hierarchical path that identifies the location of the item.
The namespace acts as a folder-like structure to organize items.
Each element in the tuple represents one level in the hierarchy.
Examples
Root level documents
```
("documents",)
```
User-specific documents
```
("documents", "user123")
```
Nested cache structure
```
("cache", "embeddings", "v1")
```
### key `instance-attribute` [¶](#langgraph.store.base.PutOp.key "Permanent link")
```
key: str
```
Unique identifier for the item within its namespace.
The key must be unique within the specific namespace to avoid conflicts.
Together with the namespace, it forms a complete path to the item.
Example
If namespace is ("documents", "user123") and key is "report1",
the full path would effectively be "documents/user123/report1"
### value `instance-attribute` [¶](#langgraph.store.base.PutOp.value "Permanent link")
```
value: dict[str, Any] | None
```
The data to store, or None to mark the item for deletion.
The value must be a dictionary with string keys and JSON-serializable values.
Setting this to None signals that the item should be deleted.
Example
{
"field1": "string value",
"field2": 123,
"nested": {"can": "contain", "any": "serializable data"}
}
### index `class-attribute` `instance-attribute` [¶](#langgraph.store.base.PutOp.index "Permanent link")
```
index: Literal[False] | list[str] | None = None
```
Controls how the item's fields are indexed for search operations.
Indexing configuration determines how the item can be found through search
* None (default): Uses the store's default indexing configuration (if provided)
* False: Disables indexing for this item
* list[str]: Specifies which json path fields to index for search
The item remains accessible through direct get() operations regardless of indexing.
When indexed, fields can be searched using natural language queries through
vector similarity search (if supported by the store implementation).
Path Syntax
* Simple field access: "field"
* Nested fields: "parent.child.grandchild"
* Array indexing:
* Specific index: "array[0]"
* Last element: "array[-1]"
* All elements (each individually): "array[\*]"
Examples
* None - Use store defaults (whole item)
* list[str] - List of fields to index
```
[
    "metadata.title",                    # Nested field access
    "context[*].content",                # Index content from all context as separate vectors
    "authors[0].name",                   # First author's name
    "revisions[-1].changes",             # Most recent revision's changes
    "sections[*].paragraphs[*].text",    # All text from all paragraphs in all sections
    "metadata.tags[*]",                  # All tags in metadata
]
```
### ttl `class-attribute` `instance-attribute` [¶](#langgraph.store.base.PutOp.ttl "Permanent link")
```
ttl: float | None = None
```
Controls the TTL (time-to-live) for the item in minutes.
If provided, and if the store you are using supports this feature, the item
will expire this many minutes after it was last accessed. The expiration timer
refreshes on both read operations (get/search) and write operations (put/update).
When the TTL expires, the item will be scheduled for deletion on a best-effort basis.
Defaults to None (no expiration).
## InvalidNamespaceError [¶](#langgraph.store.base.InvalidNamespaceError "Permanent link")
Bases: `ValueError`
Provided namespace is invalid.
## TTLConfig [¶](#langgraph.store.base.TTLConfig "Permanent link")
Bases: `TypedDict`
Configuration for TTL (time-to-live) behavior in the store.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `refresh_on_read` | `bool` | Default behavior for refreshing TTLs on read operations (GET and SEARCH). |
| `default_ttl` | `float | None` | Default TTL (time-to-live) in minutes for new items. |
| `sweep_interval_minutes` | `int | None` | Interval in minutes between TTL sweep operations. |
### refresh\_on\_read `instance-attribute` [¶](#langgraph.store.base.TTLConfig.refresh_on_read "Permanent link")
```
refresh_on_read: bool
```
Default behavior for refreshing TTLs on read operations (GET and SEARCH).
If True, TTLs will be refreshed on read operations (get/search) by default.
This can be overridden per-operation by explicitly setting refresh\_ttl.
Defaults to True if not configured.
### default\_ttl `instance-attribute` [¶](#langgraph.store.base.TTLConfig.default_ttl "Permanent link")
```
default_ttl: float | None
```
Default TTL (time-to-live) in minutes for new items.
If provided, new items will expire after this many minutes after their last access.
The expiration timer refreshes on both read and write operations.
Defaults to None (no expiration).
### sweep\_interval\_minutes `instance-attribute` [¶](#langgraph.store.base.TTLConfig.sweep_interval_minutes "Permanent link")
```
sweep_interval_minutes: int | None
```
Interval in minutes between TTL sweep operations.
If provided, the store will periodically delete expired items based on TTL.
Defaults to None (no sweeping).
## IndexConfig [¶](#langgraph.store.base.IndexConfig "Permanent link")
Bases: `TypedDict`
Configuration for indexing documents for semantic search in the store.
If not provided to the store, the store will not support vector search.
In that case, all `index` arguments to put() and `aput()` operations will be ignored.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `dims` | `int` | Number of dimensions in the embedding vectors. |
| `embed` | `Embeddings | EmbeddingsFunc | AEmbeddingsFunc | str` | Optional function to generate embeddings from text. |
| `fields` | `list[str] | None` | Fields to extract text from for embedding generation. |
### dims `instance-attribute` [¶](#langgraph.store.base.IndexConfig.dims "Permanent link")
```
dims: int
```
Number of dimensions in the embedding vectors.
Common embedding models have the following dimensions
* openai:text-embedding-3-large: 3072
* openai:text-embedding-3-small: 1536
* openai:text-embedding-ada-002: 1536
* cohere:embed-english-v3.0: 1024
* cohere:embed-english-light-v3.0: 384
* cohere:embed-multilingual-v3.0: 1024
* cohere:embed-multilingual-light-v3.0: 384
### embed `instance-attribute` [¶](#langgraph.store.base.IndexConfig.embed "Permanent link")
```
embed: Embeddings | EmbeddingsFunc | AEmbeddingsFunc | str
```
Optional function to generate embeddings from text.
Can be specified in three ways
1. A LangChain Embeddings instance
2. A synchronous embedding function (EmbeddingsFunc)
3. An asynchronous embedding function (AEmbeddingsFunc)
4. A provider string (e.g., "openai:text-embedding-3-small")
Examples
Using LangChain's initialization with InMemoryStore:
```
from langchain.embeddings import init_embeddings
from langgraph.store.memory import InMemoryStore
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": init_embeddings("openai:text-embedding-3-small")
    }
)
```
Using a custom embedding function with InMemoryStore:
```
from openai import OpenAI
from langgraph.store.memory import InMemoryStore
client = OpenAI()
def embed_texts(texts: list[str]) -> list[list[float]]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in response.data]
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": embed_texts
    }
)
```
Using an asynchronous embedding function with InMemoryStore:
```
from openai import AsyncOpenAI
from langgraph.store.memory import InMemoryStore
client = AsyncOpenAI()
async def aembed_texts(texts: list[str]) -> list[list[float]]:
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=texts
    )
    return [e.embedding for e in response.data]
store = InMemoryStore(
    index={
        "dims": 1536,
        "embed": aembed_texts
    }
)
```
### fields `instance-attribute` [¶](#langgraph.store.base.IndexConfig.fields "Permanent link")
```
fields: list[str] | None
```
Fields to extract text from for embedding generation.
Controls which parts of stored items are embedded for semantic search. Follows JSON path syntax:
```
- ["$"]: Embeds the entire JSON object as one vector  (default)
- ["field1", "field2"]: Embeds specific top-level fields
- ["parent.child"]: Embeds nested fields using dot notation
- ["array[*].field"]: Embeds field from each array element separately
```
Note
You can always override this behavior when storing an item using the
`index` parameter in the `put` or `aput` operations.
Examples
```
# Embed entire document (default)
fields=["$"]
# Embed specific fields
fields=["text", "summary"]
# Embed nested fields
fields=["metadata.title", "content.body"]
# Embed from arrays
fields=["messages[*].content"]  # Each message content separately
fields=["context[0].text"]      # First context item's text
```
Note
* Fields missing from a document are skipped
* Array notation creates separate embeddings for each element
* Complex nested paths are supported (e.g., "a.b[\*].c.d")
## BaseStore [¶](#langgraph.store.base.BaseStore "Permanent link")
Bases: `ABC`
Abstract base class for persistent key-value stores.
Stores enable persistence and memory that can be shared across threads,
scoped to user IDs, assistant IDs, or other arbitrary namespaces.
Some implementations may support semantic search capabilities through
an optional `index` configuration.
Note
Semantic search capabilities vary by implementation and are typically
disabled by default. Stores that support this feature can be configured
by providing an `index` configuration at creation time. Without this
configuration, semantic search is disabled and any `index` arguments
to storage operations will have no effect.
Similarly, TTL (time-to-live) support is disabled by default.
Subclasses must explicitly set `supports_ttl = True` to enable this feature.
Methods:
| Name | Description |
| --- | --- |
| `batch` | Execute multiple operations synchronously in a single batch. |
| `abatch` | Execute multiple operations asynchronously in a single batch. |
| `get` | Retrieve a single item. |
| `search` | Search for items within a namespace prefix. |
| `put` | Store or update an item in the store. |
| `delete` | Delete an item. |
| `list_namespaces` | List and filter namespaces in the store. |
| `aget` | Asynchronously retrieve a single item. |
| `asearch` | Asynchronously search for items within a namespace prefix. |
| `aput` | Asynchronously store or update an item in the store. |
| `adelete` | Asynchronously delete an item. |
| `alist_namespaces` | List and filter namespaces in the store asynchronously. |
### batch `abstractmethod` [¶](#langgraph.store.base.BaseStore.batch "Permanent link")
```
batch(ops: Iterable[Op]) -> list[Result]
```
Execute multiple operations synchronously in a single batch.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `ops` | `Iterable[Op]` | An iterable of operations to execute. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `list[Result]` | A list of results, where each result corresponds to an operation in the input. |
| `list[Result]` | The order of results matches the order of input operations. |
### abatch `abstractmethod` `async` [¶](#langgraph.store.base.BaseStore.abatch "Permanent link")
```
abatch(ops: Iterable[Op]) -> list[Result]
```
Execute multiple operations asynchronously in a single batch.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `ops` | `Iterable[Op]` | An iterable of operations to execute. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `list[Result]` | A list of results, where each result corresponds to an operation in the input. |
| `list[Result]` | The order of results matches the order of input operations. |
### get [¶](#langgraph.store.base.BaseStore.get "Permanent link")
```
get(
    namespace: tuple[str, ...],
    key: str,
    *,
    refresh_ttl: bool | None = None
) -> Item | None
```
Retrieve a single item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
| `refresh_ttl` | `bool | None` | Whether to refresh TTLs for the returned item. If None (default), uses the store's default refresh\_ttl setting. If no TTL is specified, this argument is ignored. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Item | None` | The retrieved item or None if not found. |
### search [¶](#langgraph.store.base.BaseStore.search "Permanent link")
```
search(
    namespace_prefix: tuple[str, ...],
    /,
    *,
    query: str | None = None,
    filter: dict[str, Any] | None = None,
    limit: int = 10,
    offset: int = 0,
    refresh_ttl: bool | None = None,
) -> list[SearchItem]
```
Search for items within a namespace prefix.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace_prefix` | `tuple[str, ...]` | Hierarchical path prefix to search within. | *required* |
| `query` | `str | None` | Optional query for natural language search. | `None` |
| `filter` | `dict[str, Any] | None` | Key-value pairs to filter results. | `None` |
| `limit` | `int` | Maximum number of items to return. | `10` |
| `offset` | `int` | Number of items to skip before returning results. | `0` |
| `refresh_ttl` | `bool | None` | Whether to refresh TTLs for the returned items. If no TTL is specified, this argument is ignored. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[SearchItem]` | List of items matching the search criteria. |
Examples
Basic filtering:
```
# Search for documents with specific metadata
results = store.search(
    ("docs",),
    filter={"type": "article", "status": "published"}
)
```
Natural language search (requires vector store implementation):
```
# Initialize store with embedding configuration
store = YourStore( # e.g., InMemoryStore, AsyncPostgresStore
    index={
        "dims": 1536,  # embedding dimensions
        "embed": your_embedding_function,  # function to create embeddings
        "fields": ["text"]  # fields to embed. Defaults to ["$"]
    }
)
# Search for semantically similar documents
results = store.search(
    ("docs",),
    query="machine learning applications in healthcare",
    filter={"type": "research_paper"},
    limit=5
)
```
Note: Natural language search support depends on your store implementation
and requires proper embedding configuration.
### put [¶](#langgraph.store.base.BaseStore.put "Permanent link")
```
put(
    namespace: tuple[str, ...],
    key: str,
    value: dict[str, Any],
    index: Literal[False] | list[str] | None = None,
    *,
    ttl: float | None | NotProvided = NOT_PROVIDED
) -> None
```
Store or update an item in the store.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item, represented as a tuple of strings. Example: ("documents", "user123") | *required* |
| `key` | `str` | Unique identifier within the namespace. Together with namespace forms the complete path to the item. | *required* |
| `value` | `dict[str, Any]` | Dictionary containing the item's data. Must contain string keys and JSON-serializable values. | *required* |
| `index` | `Literal[False] | list[str] | None` | Controls how the item's fields are indexed for search:   * None (default): Use `fields` you configured when creating the store (if any)   If you do not initialize the store with indexing capabilities,   the `index` parameter will be ignored * False: Disable indexing for this item * list[str]: List of field paths to index, supporting:   + Nested fields: "metadata.title"   + Array access: "chapters[\*].content" (each indexed separately)   + Specific indices: "authors[0].name" | `None` |
| `ttl` | `float | None | NotProvided` | Time to live in minutes. Support for this argument depends on your store adapter. If specified, the item will expire after this many minutes from when it was last accessed. None means no expiration. Expired runs will be deleted opportunistically. By default, the expiration timer refreshes on both read operations (get/search) and write operations (put/update), whenever the item is included in the operation. | `NOT_PROVIDED` |
Note
Indexing support depends on your store implementation.
If you do not initialize the store with indexing capabilities,
the `index` parameter will be ignored.
Similarly, TTL support depends on the specific store implementation.
Some implementations may not support expiration of items.
Examples
Store item. Indexing depends on how you configure the store.
```
store.put(("docs",), "report", {"memory": "Will likes ai"})
```
Do not index item for semantic search. Still accessible through get()
and search() operations but won't have a vector representation.
```
store.put(("docs",), "report", {"memory": "Will likes ai"}, index=False)
```
Index specific fields for search.
```
store.put(("docs",), "report", {"memory": "Will likes ai"}, index=["memory"])
```
### delete [¶](#langgraph.store.base.BaseStore.delete "Permanent link")
```
delete(namespace: tuple[str, ...], key: str) -> None
```
Delete an item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
### list\_namespaces [¶](#langgraph.store.base.BaseStore.list_namespaces "Permanent link")
```
list_namespaces(
    *,
    prefix: NamespacePath | None = None,
    suffix: NamespacePath | None = None,
    max_depth: int | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[tuple[str, ...]]
```
List and filter namespaces in the store.
Used to explore the organization of data,
find specific collections, or navigate the namespace hierarchy.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `prefix` | `NamespacePath | None` | Filter namespaces that start with this path. | `None` |
| `suffix` | `NamespacePath | None` | Filter namespaces that end with this path. | `None` |
| `max_depth` | `int | None` | Return namespaces up to this depth in the hierarchy. Namespaces deeper than this level will be truncated. | `None` |
| `limit` | `int` | Maximum number of namespaces to return (default 100). | `100` |
| `offset` | `int` | Number of namespaces to skip for pagination (default 0). | `0` |
Returns:
| Type | Description |
| --- | --- |
| `list[tuple[str, ...]]` | List[Tuple[str, ...]]: A list of namespace tuples that match the criteria. |
| `list[tuple[str, ...]]` | Each tuple represents a full namespace path up to `max_depth`. |
???+ example "Examples":
Setting max\_depth=3. Given the namespaces:
```
# Example if you have the following namespaces:
# ("a", "b", "c")
# ("a", "b", "d", "e")
# ("a", "b", "d", "i")
# ("a", "b", "f")
# ("a", "c", "f")
store.list_namespaces(prefix=("a", "b"), max_depth=3)
# [("a", "b", "c"), ("a", "b", "d"), ("a", "b", "f")]
```
### aget `async` [¶](#langgraph.store.base.BaseStore.aget "Permanent link")
```
aget(
    namespace: tuple[str, ...],
    key: str,
    *,
    refresh_ttl: bool | None = None
) -> Item | None
```
Asynchronously retrieve a single item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Item | None` | The retrieved item or None if not found. |
### asearch `async` [¶](#langgraph.store.base.BaseStore.asearch "Permanent link")
```
asearch(
    namespace_prefix: tuple[str, ...],
    /,
    *,
    query: str | None = None,
    filter: dict[str, Any] | None = None,
    limit: int = 10,
    offset: int = 0,
    refresh_ttl: bool | None = None,
) -> list[SearchItem]
```
Asynchronously search for items within a namespace prefix.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace_prefix` | `tuple[str, ...]` | Hierarchical path prefix to search within. | *required* |
| `query` | `str | None` | Optional query for natural language search. | `None` |
| `filter` | `dict[str, Any] | None` | Key-value pairs to filter results. | `None` |
| `limit` | `int` | Maximum number of items to return. | `10` |
| `offset` | `int` | Number of items to skip before returning results. | `0` |
| `refresh_ttl` | `bool | None` | Whether to refresh TTLs for the returned items. If None (default), uses the store's TTLConfig.refresh\_default setting. If TTLConfig is not provided or no TTL is specified, this argument is ignored. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[SearchItem]` | List of items matching the search criteria. |
Examples
Basic filtering:
```
# Search for documents with specific metadata
results = await store.asearch(
    ("docs",),
    filter={"type": "article", "status": "published"}
)
```
Natural language search (requires vector store implementation):
```
# Initialize store with embedding configuration
store = YourStore( # e.g., InMemoryStore, AsyncPostgresStore
    index={
        "dims": 1536,  # embedding dimensions
        "embed": your_embedding_function,  # function to create embeddings
        "fields": ["text"]  # fields to embed
    }
)
# Search for semantically similar documents
results = await store.asearch(
    ("docs",),
    query="machine learning applications in healthcare",
    filter={"type": "research_paper"},
    limit=5
)
```
Note: Natural language search support depends on your store implementation
and requires proper embedding configuration.
### aput `async` [¶](#langgraph.store.base.BaseStore.aput "Permanent link")
```
aput(
    namespace: tuple[str, ...],
    key: str,
    value: dict[str, Any],
    index: Literal[False] | list[str] | None = None,
    *,
    ttl: float | None | NotProvided = NOT_PROVIDED
) -> None
```
Asynchronously store or update an item in the store.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item, represented as a tuple of strings. Example: ("documents", "user123") | *required* |
| `key` | `str` | Unique identifier within the namespace. Together with namespace forms the complete path to the item. | *required* |
| `value` | `dict[str, Any]` | Dictionary containing the item's data. Must contain string keys and JSON-serializable values. | *required* |
| `index` | `Literal[False] | list[str] | None` | Controls how the item's fields are indexed for search:   * None (default): Use `fields` you configured when creating the store (if any)   If you do not initialize the store with indexing capabilities,   the `index` parameter will be ignored * False: Disable indexing for this item * list[str]: List of field paths to index, supporting:   + Nested fields: "metadata.title"   + Array access: "chapters[\*].content" (each indexed separately)   + Specific indices: "authors[0].name" | `None` |
| `ttl` | `float | None | NotProvided` | Time to live in minutes. Support for this argument depends on your store adapter. If specified, the item will expire after this many minutes from when it was last accessed. None means no expiration. Expired runs will be deleted opportunistically. By default, the expiration timer refreshes on both read operations (get/search) and write operations (put/update), whenever the item is included in the operation. | `NOT_PROVIDED` |
Note
Indexing support depends on your store implementation.
If you do not initialize the store with indexing capabilities,
the `index` parameter will be ignored.
Similarly, TTL support depends on the specific store implementation.
Some implementations may not support expiration of items.
Examples
Store item. Indexing depends on how you configure the store.
```
await store.aput(("docs",), "report", {"memory": "Will likes ai"})
```
Do not index item for semantic search. Still accessible through get()
and search() operations but won't have a vector representation.
```
await store.aput(("docs",), "report", {"memory": "Will likes ai"}, index=False)
```
Index specific fields for search (if store configured to index items):
```
await store.aput(
    ("docs",),
    "report",
    {
        "memory": "Will likes ai",
        "context": [{"content": "..."}, {"content": "..."}]
    },
    index=["memory", "context[*].content"]
)
```
### adelete `async` [¶](#langgraph.store.base.BaseStore.adelete "Permanent link")
```
adelete(namespace: tuple[str, ...], key: str) -> None
```
Asynchronously delete an item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
### alist\_namespaces `async` [¶](#langgraph.store.base.BaseStore.alist_namespaces "Permanent link")
```
alist_namespaces(
    *,
    prefix: NamespacePath | None = None,
    suffix: NamespacePath | None = None,
    max_depth: int | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[tuple[str, ...]]
```
List and filter namespaces in the store asynchronously.
Used to explore the organization of data,
find specific collections, or navigate the namespace hierarchy.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `prefix` | `NamespacePath | None` | Filter namespaces that start with this path. | `None` |
| `suffix` | `NamespacePath | None` | Filter namespaces that end with this path. | `None` |
| `max_depth` | `int | None` | Return namespaces up to this depth in the hierarchy. Namespaces deeper than this level will be truncated to this depth. | `None` |
| `limit` | `int` | Maximum number of namespaces to return (default 100). | `100` |
| `offset` | `int` | Number of namespaces to skip for pagination (default 0). | `0` |
Returns:
| Type | Description |
| --- | --- |
| `list[tuple[str, ...]]` | List[Tuple[str, ...]]: A list of namespace tuples that match the criteria. |
| `list[tuple[str, ...]]` | Each tuple represents a full namespace path up to `max_depth`. |
Examples
Setting max\_depth=3 with existing namespaces:
```
# Given the following namespaces:
# ("a", "b", "c")
# ("a", "b", "d", "e")
# ("a", "b", "d", "i")
# ("a", "b", "f")
# ("a", "c", "f")
await store.alist_namespaces(prefix=("a", "b"), max_depth=3)
# Returns: [("a", "b", "c"), ("a", "b", "d"), ("a", "b", "f")]
```
## ensure\_embeddings [¶](#langgraph.store.base.ensure_embeddings "Permanent link")
```
ensure_embeddings(
    embed: (
        Embeddings
        | EmbeddingsFunc
        | AEmbeddingsFunc
        | str
        | None
    ),
) -> Embeddings
```
Ensure that an embedding function conforms to LangChain's Embeddings interface.
This function wraps arbitrary embedding functions to make them compatible with
LangChain's Embeddings interface. It handles both synchronous and asynchronous
functions.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `embed` | `Embeddings | EmbeddingsFunc | AEmbeddingsFunc | str | None` | Either an existing Embeddings instance, or a function that converts text to embeddings. If the function is async, it will be used for both sync and async operations. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Embeddings` | An Embeddings instance that wraps the provided function(s). |
Examples
Wrap a synchronous embedding function:
```
def my_embed_fn(texts):
    return [[0.1, 0.2] for _ in texts]
embeddings = ensure_embeddings(my_embed_fn)
result = embeddings.embed_query("hello")  # Returns [0.1, 0.2]
```
Wrap an asynchronous embedding function:
```
async def my_async_fn(texts):
    return [[0.1, 0.2] for _ in texts]
embeddings = ensure_embeddings(my_async_fn)
result = await embeddings.aembed_query("hello")  # Returns [0.1, 0.2]
```
Initialize embeddings using a provider string:
```
# Requires langchain>=0.3.9 and langgraph-checkpoint>=2.0.11
embeddings = ensure_embeddings("openai:text-embedding-3-small")
result = embeddings.embed_query("hello")
```
## get\_text\_at\_path [¶](#langgraph.store.base.get_text_at_path "Permanent link")
```
get_text_at_path(
    obj: Any, path: str | list[str]
) -> list[str]
```
Extract text from an object using a path expression or pre-tokenized path.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `obj` | `Any` | The object to extract text from | *required* |
| `path` | `str | list[str]` | Either a path string or pre-tokenized path list. | *required* |
Path types handled
* Simple paths: "field1.field2"
* Array indexing: "[0]", "[\*]", "[-1]"
* Wildcards: "\*"
* Multi-field selection: "{field1,field2}"
* Nested paths in multi-field: "{field1,nested.field2}"
## tokenize\_path [¶](#langgraph.store.base.tokenize_path "Permanent link")
```
tokenize_path(path: str) -> list[str]
```
Tokenize a path into components.
Types handled
* Simple paths: "field1.field2"
* Array indexing: "[0]", "[\*]", "[-1]"
* Wildcards: "\*"
* Multi-field selection: "{field1,field2}"
Modules:
| Name | Description |
| --- | --- |
| `aio` |  |
| `base` |  |
Classes:
| Name | Description |
| --- | --- |
| `AsyncPostgresStore` | Asynchronous Postgres-backed store with optional vector search using pgvector. |
| `PoolConfig` | Connection pool settings for PostgreSQL connections. |
| `PostgresStore` | Postgres-backed store with optional vector search using pgvector. |
## AsyncPostgresStore [¶](#langgraph.store.postgres.AsyncPostgresStore "Permanent link")
Bases: `AsyncBatchedBaseStore`, `BasePostgresStore[Conn]`
Asynchronous Postgres-backed store with optional vector search using pgvector.
Examples
Basic setup and usage:
```
from langgraph.store.postgres import AsyncPostgresStore
conn_string = "postgresql://user:pass@localhost:5432/dbname"
async with AsyncPostgresStore.from_conn_string(conn_string) as store:
    await store.setup()  # Run migrations. Done once
    # Store and retrieve data
    await store.aput(("users", "123"), "prefs", {"theme": "dark"})
    item = await store.aget(("users", "123"), "prefs")
```
Vector search using LangChain embeddings:
```
from langchain.embeddings import init_embeddings
from langgraph.store.postgres import AsyncPostgresStore
conn_string = "postgresql://user:pass@localhost:5432/dbname"
async with AsyncPostgresStore.from_conn_string(
    conn_string,
    index={
        "dims": 1536,
        "embed": init_embeddings("openai:text-embedding-3-small"),
        "fields": ["text"]  # specify which fields to embed. Default is the whole serialized value
    }
) as store:
    await store.setup()  # Run migrations. Done once
    # Store documents
    await store.aput(("docs",), "doc1", {"text": "Python tutorial"})
    await store.aput(("docs",), "doc2", {"text": "TypeScript guide"})
    await store.aput(("docs",), "doc3", {"text": "Other guide"}, index=False)  # don't index
    # Search by similarity
    results = await store.asearch(("docs",), query="programming guides", limit=2)
```
Using connection pooling for better performance:
```
from langgraph.store.postgres import AsyncPostgresStore, PoolConfig
conn_string = "postgresql://user:pass@localhost:5432/dbname"
async with AsyncPostgresStore.from_conn_string(
    conn_string,
    pool_config=PoolConfig(
        min_size=5,
        max_size=20
    )
) as store:
    await store.setup()  # Run migrations. Done once
    # Use store with connection pooling...
```
Warning
Make sure to:
1. Call `setup()` before first use to create necessary tables and indexes
2. Have the pgvector extension available to use vector search
3. Use Python 3.10+ for async functionality
Note
Semantic search is disabled by default. You can enable it by providing an `index` configuration
when creating the store. Without this configuration, all `index` arguments passed to
`put` or `aput` will have no effect.
Note
If you provide a TTL configuration, you must explicitly call `start_ttl_sweeper()` to begin
the background task that removes expired items. Call `stop_ttl_sweeper()` to properly
clean up resources when you're done with the store.
Methods:
| Name | Description |
| --- | --- |
| `from_conn_string` | Create a new AsyncPostgresStore instance from a connection string. |
| `setup` | Set up the store database asynchronously. |
| `sweep_ttl` | Delete expired store items based on TTL. |
| `start_ttl_sweeper` | Periodically delete expired store items based on TTL. |
| `stop_ttl_sweeper` | Stop the TTL sweeper task if it's running. |
### from\_conn\_string `async` `classmethod` [¶](#langgraph.store.postgres.AsyncPostgresStore.from_conn_string "Permanent link")
```
from_conn_string(
    conn_string: str,
    *,
    pipeline: bool = False,
    pool_config: PoolConfig | None = None,
    index: PostgresIndexConfig | None = None,
    ttl: TTLConfig | None = None
) -> AsyncIterator[AsyncPostgresStore]
```
Create a new AsyncPostgresStore instance from a connection string.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn_string` | `str` | The Postgres connection info string. | *required* |
| `pipeline` | `bool` | Whether to use AsyncPipeline (only for single connections) | `False` |
| `pool_config` | `PoolConfig | None` | Configuration for the connection pool. If provided, will create a connection pool and use it instead of a single connection. This overrides the `pipeline` argument. | `None` |
| `index` | `PostgresIndexConfig | None` | The embedding config. | `None` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `AsyncPostgresStore` | `AsyncIterator[AsyncPostgresStore]` | A new AsyncPostgresStore instance. |
### setup `async` [¶](#langgraph.store.postgres.AsyncPostgresStore.setup "Permanent link")
```
setup() -> None
```
Set up the store database asynchronously.
This method creates the necessary tables in the Postgres database if they don't
already exist and runs database migrations. It MUST be called directly by the user
the first time the store is used.
### sweep\_ttl `async` [¶](#langgraph.store.postgres.AsyncPostgresStore.sweep_ttl "Permanent link")
```
sweep_ttl() -> int
```
Delete expired store items based on TTL.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `int` | `int` | The number of deleted items. |
### start\_ttl\_sweeper `async` [¶](#langgraph.store.postgres.AsyncPostgresStore.start_ttl_sweeper "Permanent link")
```
start_ttl_sweeper(
    sweep_interval_minutes: int | None = None,
) -> Task[None]
```
Periodically delete expired store items based on TTL.
Returns:
| Type | Description |
| --- | --- |
| `Task[None]` | Task that can be awaited or cancelled. |
### stop\_ttl\_sweeper `async` [¶](#langgraph.store.postgres.AsyncPostgresStore.stop_ttl_sweeper "Permanent link")
```
stop_ttl_sweeper(timeout: float | None = None) -> bool
```
Stop the TTL sweeper task if it's running.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `timeout` | `float | None` | Maximum time to wait for the task to stop, in seconds. If None, wait indefinitely. | `None` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `bool` | `bool` | True if the task was successfully stopped or wasn't running, False if the timeout was reached before the task stopped. |
## PoolConfig [¶](#langgraph.store.postgres.PoolConfig "Permanent link")
Bases: `TypedDict`
Connection pool settings for PostgreSQL connections.
Controls connection lifecycle and resource utilization:
- Small pools (1-5) suit low-concurrency workloads
- Larger pools handle concurrent requests but consume more resources
- Setting max\_size prevents resource exhaustion under load
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `min_size` | `int` | Minimum number of connections maintained in the pool. Defaults to 1. |
| `max_size` | `int | None` | Maximum number of connections allowed in the pool. None means unlimited. |
| `kwargs` | `dict` | Additional connection arguments passed to each connection in the pool. |
### min\_size `instance-attribute` [¶](#langgraph.store.postgres.PoolConfig.min_size "Permanent link")
```
min_size: int
```
Minimum number of connections maintained in the pool. Defaults to 1.
### max\_size `instance-attribute` [¶](#langgraph.store.postgres.PoolConfig.max_size "Permanent link")
```
max_size: int | None
```
Maximum number of connections allowed in the pool. None means unlimited.
### kwargs `instance-attribute` [¶](#langgraph.store.postgres.PoolConfig.kwargs "Permanent link")
```
kwargs: dict
```
Additional connection arguments passed to each connection in the pool.
Default kwargs set automatically:
- autocommit: True
- prepare\_threshold: 0
- row\_factory: dict\_row
## PostgresStore [¶](#langgraph.store.postgres.PostgresStore "Permanent link")
Bases: `BaseStore`, `BasePostgresStore[Conn]`
Postgres-backed store with optional vector search using pgvector.
Examples
Basic setup and usage:
```
from langgraph.store.postgres import PostgresStore
from psycopg import Connection
conn_string = "postgresql://user:pass@localhost:5432/dbname"
# Using direct connection
with Connection.connect(conn_string) as conn:
    store = PostgresStore(conn)
    store.setup() # Run migrations. Done once
    # Store and retrieve data
    store.put(("users", "123"), "prefs", {"theme": "dark"})
    item = store.get(("users", "123"), "prefs")
```
Or using the convenient from\_conn\_string helper:
```
from langgraph.store.postgres import PostgresStore
conn_string = "postgresql://user:pass@localhost:5432/dbname"
with PostgresStore.from_conn_string(conn_string) as store:
    store.setup()
    # Store and retrieve data
    store.put(("users", "123"), "prefs", {"theme": "dark"})
    item = store.get(("users", "123"), "prefs")
```
Vector search using LangChain embeddings:
```
from langchain.embeddings import init_embeddings
from langgraph.store.postgres import PostgresStore
conn_string = "postgresql://user:pass@localhost:5432/dbname"
with PostgresStore.from_conn_string(
    conn_string,
    index={
        "dims": 1536,
        "embed": init_embeddings("openai:text-embedding-3-small"),
        "fields": ["text"]  # specify which fields to embed. Default is the whole serialized value
    }
) as store:
    store.setup() # Do this once to run migrations
    # Store documents
    store.put(("docs",), "doc1", {"text": "Python tutorial"})
    store.put(("docs",), "doc2", {"text": "TypeScript guide"})
    store.put(("docs",), "doc2", {"text": "Other guide"}, index=False) # don't index
    # Search by similarity
    results = store.search(("docs",), query="programming guides", limit=2)
```
Note
Semantic search is disabled by default. You can enable it by providing an `index` configuration
when creating the store. Without this configuration, all `index` arguments passed to
`put` or `aput`will have no effect.
Warning
Make sure to call `setup()` before first use to create necessary tables and indexes.
The pgvector extension must be available to use vector search.
Note
If you provide a TTL configuration, you must explicitly call `start_ttl_sweeper()` to begin
the background thread that removes expired items. Call `stop_ttl_sweeper()` to properly
clean up resources when you're done with the store.
Methods:
| Name | Description |
| --- | --- |
| `get` | Retrieve a single item. |
| `search` | Search for items within a namespace prefix. |
| `put` | Store or update an item in the store. |
| `delete` | Delete an item. |
| `list_namespaces` | List and filter namespaces in the store. |
| `aget` | Asynchronously retrieve a single item. |
| `asearch` | Asynchronously search for items within a namespace prefix. |
| `aput` | Asynchronously store or update an item in the store. |
| `adelete` | Asynchronously delete an item. |
| `alist_namespaces` | List and filter namespaces in the store asynchronously. |
| `from_conn_string` | Create a new PostgresStore instance from a connection string. |
| `sweep_ttl` | Delete expired store items based on TTL. |
| `start_ttl_sweeper` | Periodically delete expired store items based on TTL. |
| `stop_ttl_sweeper` | Stop the TTL sweeper thread if it's running. |
| `__del__` | Ensure the TTL sweeper thread is stopped when the object is garbage collected. |
| `setup` | Set up the store database. |
### get [¶](#langgraph.store.postgres.PostgresStore.get "Permanent link")
```
get(
    namespace: tuple[str, ...],
    key: str,
    *,
    refresh_ttl: bool | None = None
) -> Item | None
```
Retrieve a single item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
| `refresh_ttl` | `bool | None` | Whether to refresh TTLs for the returned item. If None (default), uses the store's default refresh\_ttl setting. If no TTL is specified, this argument is ignored. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Item | None` | The retrieved item or None if not found. |
### search [¶](#langgraph.store.postgres.PostgresStore.search "Permanent link")
```
search(
    namespace_prefix: tuple[str, ...],
    /,
    *,
    query: str | None = None,
    filter: dict[str, Any] | None = None,
    limit: int = 10,
    offset: int = 0,
    refresh_ttl: bool | None = None,
) -> list[SearchItem]
```
Search for items within a namespace prefix.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace_prefix` | `tuple[str, ...]` | Hierarchical path prefix to search within. | *required* |
| `query` | `str | None` | Optional query for natural language search. | `None` |
| `filter` | `dict[str, Any] | None` | Key-value pairs to filter results. | `None` |
| `limit` | `int` | Maximum number of items to return. | `10` |
| `offset` | `int` | Number of items to skip before returning results. | `0` |
| `refresh_ttl` | `bool | None` | Whether to refresh TTLs for the returned items. If no TTL is specified, this argument is ignored. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[SearchItem]` | List of items matching the search criteria. |
Examples
Basic filtering:
```
# Search for documents with specific metadata
results = store.search(
    ("docs",),
    filter={"type": "article", "status": "published"}
)
```
Natural language search (requires vector store implementation):
```
# Initialize store with embedding configuration
store = YourStore( # e.g., InMemoryStore, AsyncPostgresStore
    index={
        "dims": 1536,  # embedding dimensions
        "embed": your_embedding_function,  # function to create embeddings
        "fields": ["text"]  # fields to embed. Defaults to ["$"]
    }
)
# Search for semantically similar documents
results = store.search(
    ("docs",),
    query="machine learning applications in healthcare",
    filter={"type": "research_paper"},
    limit=5
)
```
Note: Natural language search support depends on your store implementation
and requires proper embedding configuration.
### put [¶](#langgraph.store.postgres.PostgresStore.put "Permanent link")
```
put(
    namespace: tuple[str, ...],
    key: str,
    value: dict[str, Any],
    index: Literal[False] | list[str] | None = None,
    *,
    ttl: float | None | NotProvided = NOT_PROVIDED
) -> None
```
Store or update an item in the store.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item, represented as a tuple of strings. Example: ("documents", "user123") | *required* |
| `key` | `str` | Unique identifier within the namespace. Together with namespace forms the complete path to the item. | *required* |
| `value` | `dict[str, Any]` | Dictionary containing the item's data. Must contain string keys and JSON-serializable values. | *required* |
| `index` | `Literal[False] | list[str] | None` | Controls how the item's fields are indexed for search:   * None (default): Use `fields` you configured when creating the store (if any)   If you do not initialize the store with indexing capabilities,   the `index` parameter will be ignored * False: Disable indexing for this item * list[str]: List of field paths to index, supporting:   + Nested fields: "metadata.title"   + Array access: "chapters[\*].content" (each indexed separately)   + Specific indices: "authors[0].name" | `None` |
| `ttl` | `float | None | NotProvided` | Time to live in minutes. Support for this argument depends on your store adapter. If specified, the item will expire after this many minutes from when it was last accessed. None means no expiration. Expired runs will be deleted opportunistically. By default, the expiration timer refreshes on both read operations (get/search) and write operations (put/update), whenever the item is included in the operation. | `NOT_PROVIDED` |
Note
Indexing support depends on your store implementation.
If you do not initialize the store with indexing capabilities,
the `index` parameter will be ignored.
Similarly, TTL support depends on the specific store implementation.
Some implementations may not support expiration of items.
Examples
Store item. Indexing depends on how you configure the store.
```
store.put(("docs",), "report", {"memory": "Will likes ai"})
```
Do not index item for semantic search. Still accessible through get()
and search() operations but won't have a vector representation.
```
store.put(("docs",), "report", {"memory": "Will likes ai"}, index=False)
```
Index specific fields for search.
```
store.put(("docs",), "report", {"memory": "Will likes ai"}, index=["memory"])
```
### delete [¶](#langgraph.store.postgres.PostgresStore.delete "Permanent link")
```
delete(namespace: tuple[str, ...], key: str) -> None
```
Delete an item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
### list\_namespaces [¶](#langgraph.store.postgres.PostgresStore.list_namespaces "Permanent link")
```
list_namespaces(
    *,
    prefix: NamespacePath | None = None,
    suffix: NamespacePath | None = None,
    max_depth: int | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[tuple[str, ...]]
```
List and filter namespaces in the store.
Used to explore the organization of data,
find specific collections, or navigate the namespace hierarchy.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `prefix` | `NamespacePath | None` | Filter namespaces that start with this path. | `None` |
| `suffix` | `NamespacePath | None` | Filter namespaces that end with this path. | `None` |
| `max_depth` | `int | None` | Return namespaces up to this depth in the hierarchy. Namespaces deeper than this level will be truncated. | `None` |
| `limit` | `int` | Maximum number of namespaces to return (default 100). | `100` |
| `offset` | `int` | Number of namespaces to skip for pagination (default 0). | `0` |
Returns:
| Type | Description |
| --- | --- |
| `list[tuple[str, ...]]` | List[Tuple[str, ...]]: A list of namespace tuples that match the criteria. |
| `list[tuple[str, ...]]` | Each tuple represents a full namespace path up to `max_depth`. |
???+ example "Examples":
Setting max\_depth=3. Given the namespaces:
```
# Example if you have the following namespaces:
# ("a", "b", "c")
# ("a", "b", "d", "e")
# ("a", "b", "d", "i")
# ("a", "b", "f")
# ("a", "c", "f")
store.list_namespaces(prefix=("a", "b"), max_depth=3)
# [("a", "b", "c"), ("a", "b", "d"), ("a", "b", "f")]
```
### aget `async` [¶](#langgraph.store.postgres.PostgresStore.aget "Permanent link")
```
aget(
    namespace: tuple[str, ...],
    key: str,
    *,
    refresh_ttl: bool | None = None
) -> Item | None
```
Asynchronously retrieve a single item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Item | None` | The retrieved item or None if not found. |
### asearch `async` [¶](#langgraph.store.postgres.PostgresStore.asearch "Permanent link")
```
asearch(
    namespace_prefix: tuple[str, ...],
    /,
    *,
    query: str | None = None,
    filter: dict[str, Any] | None = None,
    limit: int = 10,
    offset: int = 0,
    refresh_ttl: bool | None = None,
) -> list[SearchItem]
```
Asynchronously search for items within a namespace prefix.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace_prefix` | `tuple[str, ...]` | Hierarchical path prefix to search within. | *required* |
| `query` | `str | None` | Optional query for natural language search. | `None` |
| `filter` | `dict[str, Any] | None` | Key-value pairs to filter results. | `None` |
| `limit` | `int` | Maximum number of items to return. | `10` |
| `offset` | `int` | Number of items to skip before returning results. | `0` |
| `refresh_ttl` | `bool | None` | Whether to refresh TTLs for the returned items. If None (default), uses the store's TTLConfig.refresh\_default setting. If TTLConfig is not provided or no TTL is specified, this argument is ignored. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `list[SearchItem]` | List of items matching the search criteria. |
Examples
Basic filtering:
```
# Search for documents with specific metadata
results = await store.asearch(
    ("docs",),
    filter={"type": "article", "status": "published"}
)
```
Natural language search (requires vector store implementation):
```
# Initialize store with embedding configuration
store = YourStore( # e.g., InMemoryStore, AsyncPostgresStore
    index={
        "dims": 1536,  # embedding dimensions
        "embed": your_embedding_function,  # function to create embeddings
        "fields": ["text"]  # fields to embed
    }
)
# Search for semantically similar documents
results = await store.asearch(
    ("docs",),
    query="machine learning applications in healthcare",
    filter={"type": "research_paper"},
    limit=5
)
```
Note: Natural language search support depends on your store implementation
and requires proper embedding configuration.
### aput `async` [¶](#langgraph.store.postgres.PostgresStore.aput "Permanent link")
```
aput(
    namespace: tuple[str, ...],
    key: str,
    value: dict[str, Any],
    index: Literal[False] | list[str] | None = None,
    *,
    ttl: float | None | NotProvided = NOT_PROVIDED
) -> None
```
Asynchronously store or update an item in the store.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item, represented as a tuple of strings. Example: ("documents", "user123") | *required* |
| `key` | `str` | Unique identifier within the namespace. Together with namespace forms the complete path to the item. | *required* |
| `value` | `dict[str, Any]` | Dictionary containing the item's data. Must contain string keys and JSON-serializable values. | *required* |
| `index` | `Literal[False] | list[str] | None` | Controls how the item's fields are indexed for search:   * None (default): Use `fields` you configured when creating the store (if any)   If you do not initialize the store with indexing capabilities,   the `index` parameter will be ignored * False: Disable indexing for this item * list[str]: List of field paths to index, supporting:   + Nested fields: "metadata.title"   + Array access: "chapters[\*].content" (each indexed separately)   + Specific indices: "authors[0].name" | `None` |
| `ttl` | `float | None | NotProvided` | Time to live in minutes. Support for this argument depends on your store adapter. If specified, the item will expire after this many minutes from when it was last accessed. None means no expiration. Expired runs will be deleted opportunistically. By default, the expiration timer refreshes on both read operations (get/search) and write operations (put/update), whenever the item is included in the operation. | `NOT_PROVIDED` |
Note
Indexing support depends on your store implementation.
If you do not initialize the store with indexing capabilities,
the `index` parameter will be ignored.
Similarly, TTL support depends on the specific store implementation.
Some implementations may not support expiration of items.
Examples
Store item. Indexing depends on how you configure the store.
```
await store.aput(("docs",), "report", {"memory": "Will likes ai"})
```
Do not index item for semantic search. Still accessible through get()
and search() operations but won't have a vector representation.
```
await store.aput(("docs",), "report", {"memory": "Will likes ai"}, index=False)
```
Index specific fields for search (if store configured to index items):
```
await store.aput(
    ("docs",),
    "report",
    {
        "memory": "Will likes ai",
        "context": [{"content": "..."}, {"content": "..."}]
    },
    index=["memory", "context[*].content"]
)
```
### adelete `async` [¶](#langgraph.store.postgres.PostgresStore.adelete "Permanent link")
```
adelete(namespace: tuple[str, ...], key: str) -> None
```
Asynchronously delete an item.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `namespace` | `tuple[str, ...]` | Hierarchical path for the item. | *required* |
| `key` | `str` | Unique identifier within the namespace. | *required* |
### alist\_namespaces `async` [¶](#langgraph.store.postgres.PostgresStore.alist_namespaces "Permanent link")
```
alist_namespaces(
    *,
    prefix: NamespacePath | None = None,
    suffix: NamespacePath | None = None,
    max_depth: int | None = None,
    limit: int = 100,
    offset: int = 0
) -> list[tuple[str, ...]]
```
List and filter namespaces in the store asynchronously.
Used to explore the organization of data,
find specific collections, or navigate the namespace hierarchy.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `prefix` | `NamespacePath | None` | Filter namespaces that start with this path. | `None` |
| `suffix` | `NamespacePath | None` | Filter namespaces that end with this path. | `None` |
| `max_depth` | `int | None` | Return namespaces up to this depth in the hierarchy. Namespaces deeper than this level will be truncated to this depth. | `None` |
| `limit` | `int` | Maximum number of namespaces to return (default 100). | `100` |
| `offset` | `int` | Number of namespaces to skip for pagination (default 0). | `0` |
Returns:
| Type | Description |
| --- | --- |
| `list[tuple[str, ...]]` | List[Tuple[str, ...]]: A list of namespace tuples that match the criteria. |
| `list[tuple[str, ...]]` | Each tuple represents a full namespace path up to `max_depth`. |
Examples
Setting max\_depth=3 with existing namespaces:
```
# Given the following namespaces:
# ("a", "b", "c")
# ("a", "b", "d", "e")
# ("a", "b", "d", "i")
# ("a", "b", "f")
# ("a", "c", "f")
await store.alist_namespaces(prefix=("a", "b"), max_depth=3)
# Returns: [("a", "b", "c"), ("a", "b", "d"), ("a", "b", "f")]
```
### from\_conn\_string `classmethod` [¶](#langgraph.store.postgres.PostgresStore.from_conn_string "Permanent link")
```
from_conn_string(
    conn_string: str,
    *,
    pipeline: bool = False,
    pool_config: PoolConfig | None = None,
    index: PostgresIndexConfig | None = None,
    ttl: TTLConfig | None = None
) -> Iterator[PostgresStore]
```
Create a new PostgresStore instance from a connection string.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn_string` | `str` | The Postgres connection info string. | *required* |
| `pipeline` | `bool` | whether to use Pipeline | `False` |
| `pool_config` | `PoolConfig | None` | Configuration for the connection pool. If provided, will create a connection pool and use it instead of a single connection. This overrides the `pipeline` argument. | `None` |
| `index` | `PostgresIndexConfig | None` | The index configuration for the store. | `None` |
| `ttl` | `TTLConfig | None` | The TTL configuration for the store. | `None` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `PostgresStore` | `Iterator[PostgresStore]` | A new PostgresStore instance. |
### sweep\_ttl [¶](#langgraph.store.postgres.PostgresStore.sweep_ttl "Permanent link")
```
sweep_ttl() -> int
```
Delete expired store items based on TTL.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `int` | `int` | The number of deleted items. |
### start\_ttl\_sweeper [¶](#langgraph.store.postgres.PostgresStore.start_ttl_sweeper "Permanent link")
```
start_ttl_sweeper(
    sweep_interval_minutes: int | None = None,
) -> Future[None]
```
Periodically delete expired store items based on TTL.
Returns:
| Type | Description |
| --- | --- |
| `Future[None]` | Future that can be waited on or cancelled. |
### stop\_ttl\_sweeper [¶](#langgraph.store.postgres.PostgresStore.stop_ttl_sweeper "Permanent link")
```
stop_ttl_sweeper(timeout: float | None = None) -> bool
```
Stop the TTL sweeper thread if it's running.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `timeout` | `float | None` | Maximum time to wait for the thread to stop, in seconds. If None, wait indefinitely. | `None` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `bool` | `bool` | True if the thread was successfully stopped or wasn't running, False if the timeout was reached before the thread stopped. |
### \_\_del\_\_ [¶](#langgraph.store.postgres.PostgresStore.__del__ "Permanent link")
```
__del__() -> None
```
Ensure the TTL sweeper thread is stopped when the object is garbage collected.
### setup [¶](#langgraph.store.postgres.PostgresStore.setup "Permanent link")
```
setup() -> None
```
Set up the store database.
This method creates the necessary tables in the Postgres database if they don't
already exist and runs database migrations. It MUST be called directly by the user
the first time the store is used.
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/store/)
