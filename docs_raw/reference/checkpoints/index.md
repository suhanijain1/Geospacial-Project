# Checkpointing

# Checkpointers[¶](#checkpointers "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `CheckpointMetadata` | Metadata associated with a checkpoint. |
| `Checkpoint` | State snapshot at a given point in time. |
| `BaseCheckpointSaver` | Base class for creating a graph checkpointer. |
Functions:
| Name | Description |
| --- | --- |
| `create_checkpoint` | Create a checkpoint for the given channels. |
## CheckpointMetadata [¶](#langgraph.checkpoint.base.CheckpointMetadata "Permanent link")
Bases: `TypedDict`
Metadata associated with a checkpoint.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `source` | `Literal['input', 'loop', 'update', 'fork']` | The source of the checkpoint. |
| `step` | `int` | The step number of the checkpoint. |
| `parents` | `dict[str, str]` | The IDs of the parent checkpoints. |
### source `instance-attribute` [¶](#langgraph.checkpoint.base.CheckpointMetadata.source "Permanent link")
```
source: Literal['input', 'loop', 'update', 'fork']
```
The source of the checkpoint.
* "input": The checkpoint was created from an input to invoke/stream/batch.
* "loop": The checkpoint was created from inside the pregel loop.
* "update": The checkpoint was created from a manual state update.
* "fork": The checkpoint was created as a copy of another checkpoint.
### step `instance-attribute` [¶](#langgraph.checkpoint.base.CheckpointMetadata.step "Permanent link")
```
step: int
```
The step number of the checkpoint.
-1 for the first "input" checkpoint.
0 for the first "loop" checkpoint.
... for the nth checkpoint afterwards.
### parents `instance-attribute` [¶](#langgraph.checkpoint.base.CheckpointMetadata.parents "Permanent link")
```
parents: dict[str, str]
```
The IDs of the parent checkpoints.
Mapping from checkpoint namespace to checkpoint ID.
## Checkpoint [¶](#langgraph.checkpoint.base.Checkpoint "Permanent link")
Bases: `TypedDict`
State snapshot at a given point in time.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `v` | `int` | The version of the checkpoint format. Currently 1. |
| `id` | `str` | The ID of the checkpoint. This is both unique and monotonically |
| `ts` | `str` | The timestamp of the checkpoint in ISO 8601 format. |
| `channel_values` | `dict[str, Any]` | The values of the channels at the time of the checkpoint. |
| `channel_versions` | `ChannelVersions` | The versions of the channels at the time of the checkpoint. |
| `versions_seen` | `dict[str, ChannelVersions]` | Map from node ID to map from channel name to version seen. |
| `updated_channels` | `list[str] | None` | The channels that were updated in this checkpoint. |
### v `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.v "Permanent link")
```
v: int
```
The version of the checkpoint format. Currently 1.
### id `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.id "Permanent link")
```
id: str
```
The ID of the checkpoint. This is both unique and monotonically
increasing, so can be used for sorting checkpoints from first to last.
### ts `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.ts "Permanent link")
```
ts: str
```
The timestamp of the checkpoint in ISO 8601 format.
### channel\_values `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.channel_values "Permanent link")
```
channel_values: dict[str, Any]
```
The values of the channels at the time of the checkpoint.
Mapping from channel name to deserialized channel snapshot value.
### channel\_versions `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.channel_versions "Permanent link")
```
channel_versions: ChannelVersions
```
The versions of the channels at the time of the checkpoint.
The keys are channel names and the values are monotonically increasing
version strings for each channel.
### versions\_seen `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.versions_seen "Permanent link")
```
versions_seen: dict[str, ChannelVersions]
```
Map from node ID to map from channel name to version seen.
This keeps track of the versions of the channels that each node has seen.
Used to determine which nodes to execute next.
### updated\_channels `instance-attribute` [¶](#langgraph.checkpoint.base.Checkpoint.updated_channels "Permanent link")
```
updated_channels: list[str] | None
```
The channels that were updated in this checkpoint.
## BaseCheckpointSaver [¶](#langgraph.checkpoint.base.BaseCheckpointSaver "Permanent link")
Bases: `Generic[V]`
Base class for creating a graph checkpointer.
Checkpointers allow LangGraph agents to persist their state
within and across multiple interactions.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `serde` | `SerializerProtocol` | Serializer for encoding/decoding checkpoints. |
Note
When creating a custom checkpoint saver, consider implementing async
versions to avoid blocking the main thread.
Methods:
| Name | Description |
| --- | --- |
| `get` | Fetch a checkpoint using the given configuration. |
| `get_tuple` | Fetch a checkpoint tuple using the given configuration. |
| `list` | List checkpoints that match the given criteria. |
| `put` | Store a checkpoint with its configuration and metadata. |
| `put_writes` | Store intermediate writes linked to a checkpoint. |
| `delete_thread` | Delete all checkpoints and writes associated with a specific thread ID. |
| `aget` | Asynchronously fetch a checkpoint using the given configuration. |
| `aget_tuple` | Asynchronously fetch a checkpoint tuple using the given configuration. |
| `alist` | Asynchronously list checkpoints that match the given criteria. |
| `aput` | Asynchronously store a checkpoint with its configuration and metadata. |
| `aput_writes` | Asynchronously store intermediate writes linked to a checkpoint. |
| `adelete_thread` | Delete all checkpoints and writes associated with a specific thread ID. |
| `get_next_version` | Generate the next version ID for a channel. |
### config\_specs `property` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.config_specs "Permanent link")
```
config_specs: list
```
Define the configuration options for the checkpoint saver.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `list` | `list` | List of configuration field specs. |
### get [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.get "Permanent link")
```
get(config: RunnableConfig) -> Checkpoint | None
```
Fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### get\_tuple [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.get_tuple "Permanent link")
```
get_tuple(config: RunnableConfig) -> CheckpointTuple | None
```
Fetch a checkpoint tuple using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The requested checkpoint tuple, or None if not found. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### list [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.list "Permanent link")
```
list(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[CheckpointTuple]
```
List checkpoints that match the given criteria.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria. | `None` |
| `before` | `RunnableConfig | None` | List checkpoints created before this configuration. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `Iterator[CheckpointTuple]` | Iterator[CheckpointTuple]: Iterator of matching checkpoint tuples. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### put [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.put "Permanent link")
```
put(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Store a checkpoint with its configuration and metadata.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration for the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to store. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata for the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### put\_writes [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.put_writes "Permanent link")
```
put_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Store intermediate writes linked to a checkpoint.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### delete\_thread [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.delete_thread "Permanent link")
```
delete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a specific thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID whose checkpoints should be deleted. | *required* |
### aget `async` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.aget "Permanent link")
```
aget(config: RunnableConfig) -> Checkpoint | None
```
Asynchronously fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget\_tuple `async` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.aget_tuple "Permanent link")
```
aget_tuple(
    config: RunnableConfig,
) -> CheckpointTuple | None
```
Asynchronously fetch a checkpoint tuple using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The requested checkpoint tuple, or None if not found. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### alist `async` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.alist "Permanent link")
```
alist(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[CheckpointTuple]
```
Asynchronously list checkpoints that match the given criteria.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | List checkpoints created before this configuration. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `AsyncIterator[CheckpointTuple]` | AsyncIterator[CheckpointTuple]: Async iterator of matching checkpoint tuples. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### aput `async` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.aput "Permanent link")
```
aput(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Asynchronously store a checkpoint with its configuration and metadata.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration for the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to store. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata for the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### aput\_writes `async` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.aput_writes "Permanent link")
```
aput_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Asynchronously store intermediate writes linked to a checkpoint.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### adelete\_thread `async` [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.adelete_thread "Permanent link")
```
adelete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a specific thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID whose checkpoints should be deleted. | *required* |
### get\_next\_version [¶](#langgraph.checkpoint.base.BaseCheckpointSaver.get_next_version "Permanent link")
```
get_next_version(current: V | None, channel: None) -> V
```
Generate the next version ID for a channel.
Default is to use integer versions, incrementing by 1. If you override, you can use str/int/float versions,
as long as they are monotonically increasing.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `current` | `V | None` | The current version identifier (int, float, or str). | *required* |
| `channel` | `None` | Deprecated argument, kept for backwards compatibility. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `V` | `V` | The next version identifier, which must be increasing. |
## create\_checkpoint [¶](#langgraph.checkpoint.base.create_checkpoint "Permanent link")
```
create_checkpoint(
    checkpoint: Checkpoint,
    channels: Mapping[str, ChannelProtocol] | None,
    step: int,
    *,
    id: str | None = None
) -> Checkpoint
```
Create a checkpoint for the given channels.
Classes:
| Name | Description |
| --- | --- |
| `SerializerProtocol` | Protocol for serialization and deserialization of objects. |
| `CipherProtocol` | Protocol for encryption and decryption of data. |
## SerializerProtocol [¶](#langgraph.checkpoint.serde.base.SerializerProtocol "Permanent link")
Bases: `UntypedSerializerProtocol`, `Protocol`
Protocol for serialization and deserialization of objects.
* `dumps`: Serialize an object to bytes.
* `dumps_typed`: Serialize an object to a tuple (type, bytes).
* `loads`: Deserialize an object from bytes.
* `loads_typed`: Deserialize an object from a tuple (type, bytes).
Valid implementations include the `pickle`, `json` and `orjson` modules.
## CipherProtocol [¶](#langgraph.checkpoint.serde.base.CipherProtocol "Permanent link")
Bases: `Protocol`
Protocol for encryption and decryption of data.
- `encrypt`: Encrypt plaintext.
- `decrypt`: Decrypt ciphertext.
Methods:
| Name | Description |
| --- | --- |
| `encrypt` | Encrypt plaintext. Returns a tuple (cipher name, ciphertext). |
| `decrypt` | Decrypt ciphertext. Returns the plaintext. |
### encrypt [¶](#langgraph.checkpoint.serde.base.CipherProtocol.encrypt "Permanent link")
```
encrypt(plaintext: bytes) -> tuple[str, bytes]
```
Encrypt plaintext. Returns a tuple (cipher name, ciphertext).
### decrypt [¶](#langgraph.checkpoint.serde.base.CipherProtocol.decrypt "Permanent link")
```
decrypt(ciphername: str, ciphertext: bytes) -> bytes
```
Decrypt ciphertext. Returns the plaintext.
Classes:
| Name | Description |
| --- | --- |
| `JsonPlusSerializer` | Serializer that uses ormsgpack, with a fallback to extended JSON serializer. |
## JsonPlusSerializer [¶](#langgraph.checkpoint.serde.jsonplus.JsonPlusSerializer "Permanent link")
Bases: `SerializerProtocol`
Serializer that uses ormsgpack, with a fallback to extended JSON serializer.
Classes:
| Name | Description |
| --- | --- |
| `EncryptedSerializer` | Serializer that encrypts and decrypts data using an encryption protocol. |
## EncryptedSerializer [¶](#langgraph.checkpoint.serde.encrypted.EncryptedSerializer "Permanent link")
Bases: `SerializerProtocol`
Serializer that encrypts and decrypts data using an encryption protocol.
Methods:
| Name | Description |
| --- | --- |
| `dumps_typed` | Serialize an object to a tuple (type, bytes) and encrypt the bytes. |
| `from_pycryptodome_aes` | Create an EncryptedSerializer using AES encryption. |
### dumps\_typed [¶](#langgraph.checkpoint.serde.encrypted.EncryptedSerializer.dumps_typed "Permanent link")
```
dumps_typed(obj: Any) -> tuple[str, bytes]
```
Serialize an object to a tuple (type, bytes) and encrypt the bytes.
### from\_pycryptodome\_aes `classmethod` [¶](#langgraph.checkpoint.serde.encrypted.EncryptedSerializer.from_pycryptodome_aes "Permanent link")
```
from_pycryptodome_aes(
    serde: SerializerProtocol = JsonPlusSerializer(),
    **kwargs: Any
) -> EncryptedSerializer
```
Create an EncryptedSerializer using AES encryption.
Classes:
| Name | Description |
| --- | --- |
| `InMemorySaver` | An in-memory checkpoint saver. |
| `PersistentDict` | Persistent dictionary with an API compatible with shelve and anydbm. |
## InMemorySaver [¶](#langgraph.checkpoint.memory.InMemorySaver "Permanent link")
Bases: `BaseCheckpointSaver[str]`, `AbstractContextManager`, `AbstractAsyncContextManager`
An in-memory checkpoint saver.
This checkpoint saver stores checkpoints in memory using a defaultdict.
Note
Only use `InMemorySaver` for debugging or testing purposes.
For production use cases we recommend installing [langgraph-checkpoint-postgres](https://pypi.org/project/langgraph-checkpoint-postgres/) and using `PostgresSaver` / `AsyncPostgresSaver`.
If you are using the LangGraph Platform, no checkpointer needs to be specified. The correct managed checkpointer will be used automatically.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `serde` | `SerializerProtocol | None` | The serializer to use for serializing and deserializing checkpoints. Defaults to None. | `None` |
Examples:
```
    import asyncio
    from langgraph.checkpoint.memory import InMemorySaver
    from langgraph.graph import StateGraph
    builder = StateGraph(int)
    builder.add_node("add_one", lambda x: x + 1)
    builder.set_entry_point("add_one")
    builder.set_finish_point("add_one")
    memory = InMemorySaver()
    graph = builder.compile(checkpointer=memory)
    coro = graph.ainvoke(1, {"configurable": {"thread_id": "thread-1"}})
    asyncio.run(coro)  # Output: 2
```
Methods:
| Name | Description |
| --- | --- |
| `get_tuple` | Get a checkpoint tuple from the in-memory storage. |
| `list` | List checkpoints from the in-memory storage. |
| `put` | Save a checkpoint to the in-memory storage. |
| `put_writes` | Save a list of writes to the in-memory storage. |
| `delete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `aget_tuple` | Asynchronous version of get\_tuple. |
| `alist` | Asynchronous version of list. |
| `aput` | Asynchronous version of put. |
| `aput_writes` | Asynchronous version of put\_writes. |
| `adelete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `get` | Fetch a checkpoint using the given configuration. |
| `aget` | Asynchronously fetch a checkpoint using the given configuration. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `config_specs` | `list` | Define the configuration options for the checkpoint saver. |
### config\_specs `property` [¶](#langgraph.checkpoint.memory.InMemorySaver.config_specs "Permanent link")
```
config_specs: list
```
Define the configuration options for the checkpoint saver.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `list` | `list` | List of configuration field specs. |
### get\_tuple [¶](#langgraph.checkpoint.memory.InMemorySaver.get_tuple "Permanent link")
```
get_tuple(config: RunnableConfig) -> CheckpointTuple | None
```
Get a checkpoint tuple from the in-memory storage.
This method retrieves a checkpoint tuple from the in-memory storage based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and timestamp is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
### list [¶](#langgraph.checkpoint.memory.InMemorySaver.list "Permanent link")
```
list(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[CheckpointTuple]
```
List checkpoints from the in-memory storage.
This method retrieves a list of checkpoint tuples from the in-memory storage based
on the provided criteria.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | List checkpoints created before this configuration. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `CheckpointTuple` | Iterator[CheckpointTuple]: An iterator of matching checkpoint tuples. |
### put [¶](#langgraph.checkpoint.memory.InMemorySaver.put "Permanent link")
```
put(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the in-memory storage.
This method saves a checkpoint to the in-memory storage. The checkpoint is associated
with the provided config.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New versions as of this write | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | The updated config containing the saved checkpoint's timestamp. |
### put\_writes [¶](#langgraph.checkpoint.memory.InMemorySaver.put_writes "Permanent link")
```
put_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Save a list of writes to the in-memory storage.
This method saves a list of writes to the in-memory storage. The writes are associated
with the provided config.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the writes. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | The writes to save. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `None` | The updated config containing the saved writes' timestamp. |
### delete\_thread [¶](#langgraph.checkpoint.memory.InMemorySaver.delete_thread "Permanent link")
```
delete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### aget\_tuple `async` [¶](#langgraph.checkpoint.memory.InMemorySaver.aget_tuple "Permanent link")
```
aget_tuple(
    config: RunnableConfig,
) -> CheckpointTuple | None
```
Asynchronous version of get\_tuple.
This method is an asynchronous wrapper around get\_tuple that runs the synchronous
method in a separate thread using asyncio.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
### alist `async` [¶](#langgraph.checkpoint.memory.InMemorySaver.alist "Permanent link")
```
alist(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[CheckpointTuple]
```
Asynchronous version of list.
This method is an asynchronous wrapper around list that runs the synchronous
method in a separate thread using asyncio.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | The config to use for listing the checkpoints. | *required* |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[CheckpointTuple]` | AsyncIterator[CheckpointTuple]: An asynchronous iterator of checkpoint tuples. |
### aput `async` [¶](#langgraph.checkpoint.memory.InMemorySaver.aput "Permanent link")
```
aput(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Asynchronous version of put.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New versions as of this write | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | The updated config containing the saved checkpoint's timestamp. |
### aput\_writes `async` [¶](#langgraph.checkpoint.memory.InMemorySaver.aput_writes "Permanent link")
```
aput_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Asynchronous version of put\_writes.
This method is an asynchronous wrapper around put\_writes that runs the synchronous
method in a separate thread using asyncio.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the writes. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | The writes to save, each as a (channel, value) pair. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### adelete\_thread `async` [¶](#langgraph.checkpoint.memory.InMemorySaver.adelete_thread "Permanent link")
```
adelete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### get [¶](#langgraph.checkpoint.memory.InMemorySaver.get "Permanent link")
```
get(config: RunnableConfig) -> Checkpoint | None
```
Fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget `async` [¶](#langgraph.checkpoint.memory.InMemorySaver.aget "Permanent link")
```
aget(config: RunnableConfig) -> Checkpoint | None
```
Asynchronously fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
## PersistentDict [¶](#langgraph.checkpoint.memory.PersistentDict "Permanent link")
Bases: `defaultdict`
Persistent dictionary with an API compatible with shelve and anydbm.
The dict is kept in memory, so the dictionary operations run as fast as
a regular dictionary.
Write to disk is delayed until close or sync (similar to gdbm's fast mode).
Input file format is automatically discovered.
Output file format is selectable between pickle, json, and csv.
All three serialization formats are backed by fast C implementations.
Adapted from <https://code.activestate.com/recipes/576642-persistent-dict-with-multiple-standard-file-format/>
Methods:
| Name | Description |
| --- | --- |
| `sync` | Write dict to disk |
### sync [¶](#langgraph.checkpoint.memory.PersistentDict.sync "Permanent link")
```
sync() -> None
```
Write dict to disk
Modules:
| Name | Description |
| --- | --- |
| `aio` |  |
| `utils` |  |
Classes:
| Name | Description |
| --- | --- |
| `SqliteSaver` | A checkpoint saver that stores checkpoints in a SQLite database. |
## SqliteSaver [¶](#langgraph.checkpoint.sqlite.SqliteSaver "Permanent link")
Bases: `BaseCheckpointSaver[str]`
A checkpoint saver that stores checkpoints in a SQLite database.
Note
This class is meant for lightweight, synchronous use cases
(demos and small projects) and does not
scale to multiple threads.
For a similar sqlite saver with `async` support,
consider using [AsyncSqliteSaver](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">AsyncSqliteSaver</span>").
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn` | `Connection` | The SQLite database connection. | *required* |
| `serde` | `Optional[SerializerProtocol]` | The serializer to use for serializing and deserializing checkpoints. Defaults to JsonPlusSerializerCompat. | `None` |
Examples:
```
>>> import sqlite3
>>> from langgraph.checkpoint.sqlite import SqliteSaver
>>> from langgraph.graph import StateGraph
>>>
>>> builder = StateGraph(int)
>>> builder.add_node("add_one", lambda x: x + 1)
>>> builder.set_entry_point("add_one")
>>> builder.set_finish_point("add_one")
>>> # Create a new SqliteSaver instance
>>> # Note: check_same_thread=False is OK as the implementation uses a lock
>>> # to ensure thread safety.
>>> conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
>>> memory = SqliteSaver(conn)
>>> graph = builder.compile(checkpointer=memory)
>>> config = {"configurable": {"thread_id": "1"}}
>>> graph.get_state(config)
>>> result = graph.invoke(3, config)
>>> graph.get_state(config)
StateSnapshot(values=4, next=(), config={'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '0c62ca34-ac19-445d-bbb0-5b4984975b2a'}}, parent_config=None)
```
Methods:
| Name | Description |
| --- | --- |
| `from_conn_string` | Create a new SqliteSaver instance from a connection string. |
| `setup` | Set up the checkpoint database. |
| `cursor` | Get a cursor for the SQLite database. |
| `get_tuple` | Get a checkpoint tuple from the database. |
| `list` | List checkpoints from the database. |
| `put` | Save a checkpoint to the database. |
| `put_writes` | Store intermediate writes linked to a checkpoint. |
| `delete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `aget_tuple` | Get a checkpoint tuple from the database asynchronously. |
| `alist` | List checkpoints from the database asynchronously. |
| `aput` | Save a checkpoint to the database asynchronously. |
| `get_next_version` | Generate the next version ID for a channel. |
| `get` | Fetch a checkpoint using the given configuration. |
| `aget` | Asynchronously fetch a checkpoint using the given configuration. |
| `aput_writes` | Asynchronously store intermediate writes linked to a checkpoint. |
| `adelete_thread` | Delete all checkpoints and writes associated with a specific thread ID. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `config_specs` | `list` | Define the configuration options for the checkpoint saver. |
### config\_specs `property` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.config_specs "Permanent link")
```
config_specs: list
```
Define the configuration options for the checkpoint saver.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `list` | `list` | List of configuration field specs. |
### from\_conn\_string `classmethod` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.from_conn_string "Permanent link")
```
from_conn_string(conn_string: str) -> Iterator[SqliteSaver]
```
Create a new SqliteSaver instance from a connection string.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn_string` | `str` | The SQLite connection string. | *required* |
Yields:
| Name | Type | Description |
| --- | --- | --- |
| `SqliteSaver` | `SqliteSaver` | A new SqliteSaver instance. |
Examples:
```
In memory:
    with SqliteSaver.from_conn_string(":memory:") as memory:
        ...
To disk:
    with SqliteSaver.from_conn_string("checkpoints.sqlite") as memory:
        ...
```
### setup [¶](#langgraph.checkpoint.sqlite.SqliteSaver.setup "Permanent link")
```
setup() -> None
```
Set up the checkpoint database.
This method creates the necessary tables in the SQLite database if they don't
already exist. It is called automatically when needed and should not be called
directly by the user.
### cursor [¶](#langgraph.checkpoint.sqlite.SqliteSaver.cursor "Permanent link")
```
cursor(transaction: bool = True) -> Iterator[Cursor]
```
Get a cursor for the SQLite database.
This method returns a cursor for the SQLite database. It is used internally
by the SqliteSaver and should not be called directly by the user.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `transaction` | `bool` | Whether to commit the transaction when the cursor is closed. Defaults to True. | `True` |
Yields:
| Type | Description |
| --- | --- |
| `Cursor` | sqlite3.Cursor: A cursor for the SQLite database. |
### get\_tuple [¶](#langgraph.checkpoint.sqlite.SqliteSaver.get_tuple "Permanent link")
```
get_tuple(config: RunnableConfig) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database.
This method retrieves a checkpoint tuple from the SQLite database based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
Examples:
```
Basic:
>>> config = {"configurable": {"thread_id": "1"}}
>>> checkpoint_tuple = memory.get_tuple(config)
>>> print(checkpoint_tuple)
CheckpointTuple(...)
With checkpoint ID:
>>> config = {
...    "configurable": {
...        "thread_id": "1",
...        "checkpoint_ns": "",
...        "checkpoint_id": "1ef4f797-8335-6428-8001-8a1503f9b875",
...    }
... }
>>> checkpoint_tuple = memory.get_tuple(config)
>>> print(checkpoint_tuple)
CheckpointTuple(...)
```
### list [¶](#langgraph.checkpoint.sqlite.SqliteSaver.list "Permanent link")
```
list(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[CheckpointTuple]
```
List checkpoints from the database.
This method retrieves a list of checkpoint tuples from the SQLite database based
on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | The config to use for listing the checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. Defaults to None. | `None` |
| `before` | `RunnableConfig | None` | If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None. | `None` |
| `limit` | `int | None` | The maximum number of checkpoints to return. Defaults to None. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `CheckpointTuple` | Iterator[CheckpointTuple]: An iterator of checkpoint tuples. |
Examples:
```
>>> from langgraph.checkpoint.sqlite import SqliteSaver
>>> with SqliteSaver.from_conn_string(":memory:") as memory:
... # Run a graph, then list the checkpoints
>>>     config = {"configurable": {"thread_id": "1"}}
>>>     checkpoints = list(memory.list(config, limit=2))
>>> print(checkpoints)
[CheckpointTuple(...), CheckpointTuple(...)]
```
```
>>> config = {"configurable": {"thread_id": "1"}}
>>> before = {"configurable": {"checkpoint_id": "1ef4f797-8335-6428-8001-8a1503f9b875"}}
>>> with SqliteSaver.from_conn_string(":memory:") as memory:
... # Run a graph, then list the checkpoints
>>>     checkpoints = list(memory.list(config, before=before))
>>> print(checkpoints)
[CheckpointTuple(...), ...]
```
### put [¶](#langgraph.checkpoint.sqlite.SqliteSaver.put "Permanent link")
```
put(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database.
This method saves a checkpoint to the SQLite database. The checkpoint is associated
with the provided config and its parent config (if any).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
Examples:
```
>>> from langgraph.checkpoint.sqlite import SqliteSaver
>>> with SqliteSaver.from_conn_string(":memory:") as memory:
>>>     config = {"configurable": {"thread_id": "1", "checkpoint_ns": ""}}
>>>     checkpoint = {"ts": "2024-05-04T06:32:42.235444+00:00", "id": "1ef4f797-8335-6428-8001-8a1503f9b875", "channel_values": {"key": "value"}}
>>>     saved_config = memory.put(config, checkpoint, {"source": "input", "step": 1, "writes": {"key": "value"}}, {})
>>> print(saved_config)
{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef4f797-8335-6428-8001-8a1503f9b875'}}
```
### put\_writes [¶](#langgraph.checkpoint.sqlite.SqliteSaver.put_writes "Permanent link")
```
put_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Store intermediate writes linked to a checkpoint.
This method saves intermediate writes associated with a checkpoint to the SQLite database.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store, each as (channel, value) pair. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
### delete\_thread [¶](#langgraph.checkpoint.sqlite.SqliteSaver.delete_thread "Permanent link")
```
delete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### aget\_tuple `async` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.aget_tuple "Permanent link")
```
aget_tuple(
    config: RunnableConfig,
) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database asynchronously.
Note
This async method is not supported by the SqliteSaver class.
Use get\_tuple() instead, or consider using [AsyncSqliteSaver](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">AsyncSqliteSaver</span>").
### alist `async` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.alist "Permanent link")
```
alist(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[CheckpointTuple]
```
List checkpoints from the database asynchronously.
Note
This async method is not supported by the SqliteSaver class.
Use list() instead, or consider using [AsyncSqliteSaver](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">AsyncSqliteSaver</span>").
### aput `async` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.aput "Permanent link")
```
aput(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database asynchronously.
Note
This async method is not supported by the SqliteSaver class.
Use put() instead, or consider using [AsyncSqliteSaver](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver "<code class=\"doc-symbol doc-symbol-heading doc-symbol-class\"></code>            <span class=\"doc doc-object-name doc-class-name\">AsyncSqliteSaver</span>").
### get\_next\_version [¶](#langgraph.checkpoint.sqlite.SqliteSaver.get_next_version "Permanent link")
```
get_next_version(current: str | None, channel: None) -> str
```
Generate the next version ID for a channel.
This method creates a new version identifier for a channel based on its current version.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `current` | `Optional[str]` | The current version identifier of the channel. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | The next version identifier, which is guaranteed to be monotonically increasing. |
### get [¶](#langgraph.checkpoint.sqlite.SqliteSaver.get "Permanent link")
```
get(config: RunnableConfig) -> Checkpoint | None
```
Fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget `async` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.aget "Permanent link")
```
aget(config: RunnableConfig) -> Checkpoint | None
```
Asynchronously fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aput\_writes `async` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.aput_writes "Permanent link")
```
aput_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Asynchronously store intermediate writes linked to a checkpoint.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### adelete\_thread `async` [¶](#langgraph.checkpoint.sqlite.SqliteSaver.adelete_thread "Permanent link")
```
adelete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a specific thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID whose checkpoints should be deleted. | *required* |
Classes:
| Name | Description |
| --- | --- |
| `AsyncSqliteSaver` | An asynchronous checkpoint saver that stores checkpoints in a SQLite database. |
## AsyncSqliteSaver [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver "Permanent link")
Bases: `BaseCheckpointSaver[str]`
An asynchronous checkpoint saver that stores checkpoints in a SQLite database.
This class provides an asynchronous interface for saving and retrieving checkpoints
using a SQLite database. It's designed for use in asynchronous environments and
offers better performance for I/O-bound operations compared to synchronous alternatives.
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `conn` | `Connection` | The asynchronous SQLite database connection. |
| `serde` | `SerializerProtocol` | The serializer used for encoding/decoding checkpoints. |
Tip
Requires the [aiosqlite](https://pypi.org/project/aiosqlite/) package.
Install it with `pip install aiosqlite`.
Warning
While this class supports asynchronous checkpointing, it is not recommended
for production workloads due to limitations in SQLite's write performance.
For production use, consider a more robust database like PostgreSQL.
Tip
Remember to **close the database connection** after executing your code,
otherwise, you may see the graph "hang" after execution (since the program
will not exit until the connection is closed).
The easiest way is to use the `async with` statement as shown in the examples.
```
async with AsyncSqliteSaver.from_conn_string("checkpoints.sqlite") as saver:
    # Your code here
    graph = builder.compile(checkpointer=saver)
    config = {"configurable": {"thread_id": "thread-1"}}
    async for event in graph.astream_events(..., config, version="v1"):
        print(event)
```
Examples:
Usage within StateGraph:
```
>>> import asyncio
>>>
>>> from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
>>> from langgraph.graph import StateGraph
>>>
>>> async def main():
>>>     builder = StateGraph(int)
>>>     builder.add_node("add_one", lambda x: x + 1)
>>>     builder.set_entry_point("add_one")
>>>     builder.set_finish_point("add_one")
>>>     async with AsyncSqliteSaver.from_conn_string("checkpoints.db") as memory:
>>>         graph = builder.compile(checkpointer=memory)
>>>         coro = graph.ainvoke(1, {"configurable": {"thread_id": "thread-1"}})
>>>         print(await asyncio.gather(coro))
>>>
>>> asyncio.run(main())
Output: [2]
```
Raw usage:
```
>>> import asyncio
>>> import aiosqlite
>>> from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver
>>>
>>> async def main():
>>>     async with aiosqlite.connect("checkpoints.db") as conn:
...         saver = AsyncSqliteSaver(conn)
...         config = {"configurable": {"thread_id": "1", "checkpoint_ns": ""}}
...         checkpoint = {"ts": "2023-05-03T10:00:00Z", "data": {"key": "value"}, "id": "0c62ca34-ac19-445d-bbb0-5b4984975b2a"}
...         saved_config = await saver.aput(config, checkpoint, {}, {})
...         print(saved_config)
>>> asyncio.run(main())
{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '0c62ca34-ac19-445d-bbb0-5b4984975b2a'}}
```
Methods:
| Name | Description |
| --- | --- |
| `from_conn_string` | Create a new AsyncSqliteSaver instance from a connection string. |
| `get_tuple` | Get a checkpoint tuple from the database. |
| `list` | List checkpoints from the database asynchronously. |
| `put` | Save a checkpoint to the database. |
| `delete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `setup` | Set up the checkpoint database asynchronously. |
| `aget_tuple` | Get a checkpoint tuple from the database asynchronously. |
| `alist` | List checkpoints from the database asynchronously. |
| `aput` | Save a checkpoint to the database asynchronously. |
| `aput_writes` | Store intermediate writes linked to a checkpoint asynchronously. |
| `adelete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `get_next_version` | Generate the next version ID for a channel. |
| `get` | Fetch a checkpoint using the given configuration. |
| `aget` | Asynchronously fetch a checkpoint using the given configuration. |
### config\_specs `property` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.config_specs "Permanent link")
```
config_specs: list
```
Define the configuration options for the checkpoint saver.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `list` | `list` | List of configuration field specs. |
### from\_conn\_string `async` `classmethod` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.from_conn_string "Permanent link")
```
from_conn_string(
    conn_string: str,
) -> AsyncIterator[AsyncSqliteSaver]
```
Create a new AsyncSqliteSaver instance from a connection string.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn_string` | `str` | The SQLite connection string. | *required* |
Yields:
| Name | Type | Description |
| --- | --- | --- |
| `AsyncSqliteSaver` | `AsyncIterator[AsyncSqliteSaver]` | A new AsyncSqliteSaver instance. |
### get\_tuple [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.get_tuple "Permanent link")
```
get_tuple(config: RunnableConfig) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database.
This method retrieves a checkpoint tuple from the SQLite database based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
### list [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.list "Permanent link")
```
list(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[CheckpointTuple]
```
List checkpoints from the database asynchronously.
This method retrieves a list of checkpoint tuples from the SQLite database based
on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `CheckpointTuple` | Iterator[CheckpointTuple]: An iterator of matching checkpoint tuples. |
### put [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.put "Permanent link")
```
put(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database.
This method saves a checkpoint to the SQLite database. The checkpoint is associated
with the provided config and its parent config (if any).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
### delete\_thread [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.delete_thread "Permanent link")
```
delete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### setup `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.setup "Permanent link")
```
setup() -> None
```
Set up the checkpoint database asynchronously.
This method creates the necessary tables in the SQLite database if they don't
already exist. It is called automatically when needed and should not be called
directly by the user.
### aget\_tuple `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.aget_tuple "Permanent link")
```
aget_tuple(
    config: RunnableConfig,
) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database asynchronously.
This method retrieves a checkpoint tuple from the SQLite database based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and checkpoint ID is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
### alist `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.alist "Permanent link")
```
alist(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[CheckpointTuple]
```
List checkpoints from the database asynchronously.
This method retrieves a list of checkpoint tuples from the SQLite database based
on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[CheckpointTuple]` | AsyncIterator[CheckpointTuple]: An asynchronous iterator of matching checkpoint tuples. |
### aput `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.aput "Permanent link")
```
aput(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database asynchronously.
This method saves a checkpoint to the SQLite database. The checkpoint is associated
with the provided config and its parent config (if any).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
### aput\_writes `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.aput_writes "Permanent link")
```
aput_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Store intermediate writes linked to a checkpoint asynchronously.
This method saves intermediate writes associated with a checkpoint to the database.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store, each as (channel, value) pair. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
### adelete\_thread `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.adelete_thread "Permanent link")
```
adelete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### get\_next\_version [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.get_next_version "Permanent link")
```
get_next_version(current: str | None, channel: None) -> str
```
Generate the next version ID for a channel.
This method creates a new version identifier for a channel based on its current version.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `current` | `Optional[str]` | The current version identifier of the channel. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `str` | `str` | The next version identifier, which is guaranteed to be monotonically increasing. |
### get [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.get "Permanent link")
```
get(config: RunnableConfig) -> Checkpoint | None
```
Fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget `async` [¶](#langgraph.checkpoint.sqlite.aio.AsyncSqliteSaver.aget "Permanent link")
```
aget(config: RunnableConfig) -> Checkpoint | None
```
Asynchronously fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
Classes:
| Name | Description |
| --- | --- |
| `PostgresSaver` | Checkpointer that stores checkpoints in a Postgres database. |
## PostgresSaver [¶](#langgraph.checkpoint.postgres.PostgresSaver "Permanent link")
Bases: `BasePostgresSaver`
Checkpointer that stores checkpoints in a Postgres database.
Methods:
| Name | Description |
| --- | --- |
| `from_conn_string` | Create a new PostgresSaver instance from a connection string. |
| `setup` | Set up the checkpoint database asynchronously. |
| `list` | List checkpoints from the database. |
| `get_tuple` | Get a checkpoint tuple from the database. |
| `put` | Save a checkpoint to the database. |
| `put_writes` | Store intermediate writes linked to a checkpoint. |
| `delete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `get` | Fetch a checkpoint using the given configuration. |
| `aget` | Asynchronously fetch a checkpoint using the given configuration. |
| `aget_tuple` | Asynchronously fetch a checkpoint tuple using the given configuration. |
| `alist` | Asynchronously list checkpoints that match the given criteria. |
| `aput` | Asynchronously store a checkpoint with its configuration and metadata. |
| `aput_writes` | Asynchronously store intermediate writes linked to a checkpoint. |
| `adelete_thread` | Delete all checkpoints and writes associated with a specific thread ID. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `config_specs` | `list` | Define the configuration options for the checkpoint saver. |
### config\_specs `property` [¶](#langgraph.checkpoint.postgres.PostgresSaver.config_specs "Permanent link")
```
config_specs: list
```
Define the configuration options for the checkpoint saver.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `list` | `list` | List of configuration field specs. |
### from\_conn\_string `classmethod` [¶](#langgraph.checkpoint.postgres.PostgresSaver.from_conn_string "Permanent link")
```
from_conn_string(
    conn_string: str, *, pipeline: bool = False
) -> Iterator[PostgresSaver]
```
Create a new PostgresSaver instance from a connection string.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn_string` | `str` | The Postgres connection info string. | *required* |
| `pipeline` | `bool` | whether to use Pipeline | `False` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `PostgresSaver` | `Iterator[PostgresSaver]` | A new PostgresSaver instance. |
### setup [¶](#langgraph.checkpoint.postgres.PostgresSaver.setup "Permanent link")
```
setup() -> None
```
Set up the checkpoint database asynchronously.
This method creates the necessary tables in the Postgres database if they don't
already exist and runs database migrations. It MUST be called directly by the user
the first time checkpointer is used.
### list [¶](#langgraph.checkpoint.postgres.PostgresSaver.list "Permanent link")
```
list(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[CheckpointTuple]
```
List checkpoints from the database.
This method retrieves a list of checkpoint tuples from the Postgres database based
on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | The config to use for listing the checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. Defaults to None. | `None` |
| `before` | `RunnableConfig | None` | If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None. | `None` |
| `limit` | `int | None` | The maximum number of checkpoints to return. Defaults to None. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `CheckpointTuple` | Iterator[CheckpointTuple]: An iterator of checkpoint tuples. |
Examples:
```
>>> from langgraph.checkpoint.postgres import PostgresSaver
>>> DB_URI = "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable"
>>> with PostgresSaver.from_conn_string(DB_URI) as memory:
... # Run a graph, then list the checkpoints
>>>     config = {"configurable": {"thread_id": "1"}}
>>>     checkpoints = list(memory.list(config, limit=2))
>>> print(checkpoints)
[CheckpointTuple(...), CheckpointTuple(...)]
```
```
>>> config = {"configurable": {"thread_id": "1"}}
>>> before = {"configurable": {"checkpoint_id": "1ef4f797-8335-6428-8001-8a1503f9b875"}}
>>> with PostgresSaver.from_conn_string(DB_URI) as memory:
... # Run a graph, then list the checkpoints
>>>     checkpoints = list(memory.list(config, before=before))
>>> print(checkpoints)
[CheckpointTuple(...), ...]
```
### get\_tuple [¶](#langgraph.checkpoint.postgres.PostgresSaver.get_tuple "Permanent link")
```
get_tuple(config: RunnableConfig) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database.
This method retrieves a checkpoint tuple from the Postgres database based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and timestamp is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
Examples:
```
Basic:
>>> config = {"configurable": {"thread_id": "1"}}
>>> checkpoint_tuple = memory.get_tuple(config)
>>> print(checkpoint_tuple)
CheckpointTuple(...)
With timestamp:
>>> config = {
...    "configurable": {
...        "thread_id": "1",
...        "checkpoint_ns": "",
...        "checkpoint_id": "1ef4f797-8335-6428-8001-8a1503f9b875",
...    }
... }
>>> checkpoint_tuple = memory.get_tuple(config)
>>> print(checkpoint_tuple)
CheckpointTuple(...)
```
### put [¶](#langgraph.checkpoint.postgres.PostgresSaver.put "Permanent link")
```
put(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database.
This method saves a checkpoint to the Postgres database. The checkpoint is associated
with the provided config and its parent config (if any).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
Examples:
```
>>> from langgraph.checkpoint.postgres import PostgresSaver
>>> DB_URI = "postgres://postgres:postgres@localhost:5432/postgres?sslmode=disable"
>>> with PostgresSaver.from_conn_string(DB_URI) as memory:
>>>     config = {"configurable": {"thread_id": "1", "checkpoint_ns": ""}}
>>>     checkpoint = {"ts": "2024-05-04T06:32:42.235444+00:00", "id": "1ef4f797-8335-6428-8001-8a1503f9b875", "channel_values": {"key": "value"}}
>>>     saved_config = memory.put(config, checkpoint, {"source": "input", "step": 1, "writes": {"key": "value"}}, {})
>>> print(saved_config)
{'configurable': {'thread_id': '1', 'checkpoint_ns': '', 'checkpoint_id': '1ef4f797-8335-6428-8001-8a1503f9b875'}}
```
### put\_writes [¶](#langgraph.checkpoint.postgres.PostgresSaver.put_writes "Permanent link")
```
put_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Store intermediate writes linked to a checkpoint.
This method saves intermediate writes associated with a checkpoint to the Postgres database.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
### delete\_thread [¶](#langgraph.checkpoint.postgres.PostgresSaver.delete_thread "Permanent link")
```
delete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### get [¶](#langgraph.checkpoint.postgres.PostgresSaver.get "Permanent link")
```
get(config: RunnableConfig) -> Checkpoint | None
```
Fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget `async` [¶](#langgraph.checkpoint.postgres.PostgresSaver.aget "Permanent link")
```
aget(config: RunnableConfig) -> Checkpoint | None
```
Asynchronously fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget\_tuple `async` [¶](#langgraph.checkpoint.postgres.PostgresSaver.aget_tuple "Permanent link")
```
aget_tuple(
    config: RunnableConfig,
) -> CheckpointTuple | None
```
Asynchronously fetch a checkpoint tuple using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The requested checkpoint tuple, or None if not found. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### alist `async` [¶](#langgraph.checkpoint.postgres.PostgresSaver.alist "Permanent link")
```
alist(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[CheckpointTuple]
```
Asynchronously list checkpoints that match the given criteria.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | List checkpoints created before this configuration. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Returns:
| Type | Description |
| --- | --- |
| `AsyncIterator[CheckpointTuple]` | AsyncIterator[CheckpointTuple]: Async iterator of matching checkpoint tuples. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### aput `async` [¶](#langgraph.checkpoint.postgres.PostgresSaver.aput "Permanent link")
```
aput(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Asynchronously store a checkpoint with its configuration and metadata.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration for the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to store. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata for the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### aput\_writes `async` [¶](#langgraph.checkpoint.postgres.PostgresSaver.aput_writes "Permanent link")
```
aput_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Asynchronously store intermediate writes linked to a checkpoint.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
Raises:
| Type | Description |
| --- | --- |
| `NotImplementedError` | Implement this method in your custom checkpoint saver. |
### adelete\_thread `async` [¶](#langgraph.checkpoint.postgres.PostgresSaver.adelete_thread "Permanent link")
```
adelete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a specific thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID whose checkpoints should be deleted. | *required* |
Classes:
| Name | Description |
| --- | --- |
| `AsyncPostgresSaver` | Asynchronous checkpointer that stores checkpoints in a Postgres database. |
## AsyncPostgresSaver [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver "Permanent link")
Bases: `BasePostgresSaver`
Asynchronous checkpointer that stores checkpoints in a Postgres database.
Methods:
| Name | Description |
| --- | --- |
| `from_conn_string` | Create a new AsyncPostgresSaver instance from a connection string. |
| `setup` | Set up the checkpoint database asynchronously. |
| `alist` | List checkpoints from the database asynchronously. |
| `aget_tuple` | Get a checkpoint tuple from the database asynchronously. |
| `aput` | Save a checkpoint to the database asynchronously. |
| `aput_writes` | Store intermediate writes linked to a checkpoint asynchronously. |
| `adelete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `list` | List checkpoints from the database. |
| `get_tuple` | Get a checkpoint tuple from the database. |
| `put` | Save a checkpoint to the database. |
| `put_writes` | Store intermediate writes linked to a checkpoint. |
| `delete_thread` | Delete all checkpoints and writes associated with a thread ID. |
| `get` | Fetch a checkpoint using the given configuration. |
| `aget` | Asynchronously fetch a checkpoint using the given configuration. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `config_specs` | `list` | Define the configuration options for the checkpoint saver. |
### config\_specs `property` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.config_specs "Permanent link")
```
config_specs: list
```
Define the configuration options for the checkpoint saver.
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `list` | `list` | List of configuration field specs. |
### from\_conn\_string `async` `classmethod` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.from_conn_string "Permanent link")
```
from_conn_string(
    conn_string: str,
    *,
    pipeline: bool = False,
    serde: SerializerProtocol | None = None
) -> AsyncIterator[AsyncPostgresSaver]
```
Create a new AsyncPostgresSaver instance from a connection string.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `conn_string` | `str` | The Postgres connection info string. | *required* |
| `pipeline` | `bool` | whether to use AsyncPipeline | `False` |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `AsyncPostgresSaver` | `AsyncIterator[AsyncPostgresSaver]` | A new AsyncPostgresSaver instance. |
### setup `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.setup "Permanent link")
```
setup() -> None
```
Set up the checkpoint database asynchronously.
This method creates the necessary tables in the Postgres database if they don't
already exist and runs database migrations. It MUST be called directly by the user
the first time checkpointer is used.
### alist `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.alist "Permanent link")
```
alist(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> AsyncIterator[CheckpointTuple]
```
List checkpoints from the database asynchronously.
This method retrieves a list of checkpoint tuples from the Postgres database based
on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `AsyncIterator[CheckpointTuple]` | AsyncIterator[CheckpointTuple]: An asynchronous iterator of matching checkpoint tuples. |
### aget\_tuple `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.aget_tuple "Permanent link")
```
aget_tuple(
    config: RunnableConfig,
) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database asynchronously.
This method retrieves a checkpoint tuple from the Postgres database based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and "checkpoint\_id" is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
### aput `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.aput "Permanent link")
```
aput(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database asynchronously.
This method saves a checkpoint to the Postgres database. The checkpoint is associated
with the provided config and its parent config (if any).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
### aput\_writes `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.aput_writes "Permanent link")
```
aput_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Store intermediate writes linked to a checkpoint asynchronously.
This method saves intermediate writes associated with a checkpoint to the database.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store, each as (channel, value) pair. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
### adelete\_thread `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.adelete_thread "Permanent link")
```
adelete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### list [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.list "Permanent link")
```
list(
    config: RunnableConfig | None,
    *,
    filter: dict[str, Any] | None = None,
    before: RunnableConfig | None = None,
    limit: int | None = None
) -> Iterator[CheckpointTuple]
```
List checkpoints from the database.
This method retrieves a list of checkpoint tuples from the Postgres database based
on the provided config. The checkpoints are ordered by checkpoint ID in descending order (newest first).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig | None` | Base configuration for filtering checkpoints. | *required* |
| `filter` | `dict[str, Any] | None` | Additional filtering criteria for metadata. | `None` |
| `before` | `RunnableConfig | None` | If provided, only checkpoints before the specified checkpoint ID are returned. Defaults to None. | `None` |
| `limit` | `int | None` | Maximum number of checkpoints to return. | `None` |
Yields:
| Type | Description |
| --- | --- |
| `CheckpointTuple` | Iterator[CheckpointTuple]: An iterator of matching checkpoint tuples. |
### get\_tuple [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.get_tuple "Permanent link")
```
get_tuple(config: RunnableConfig) -> CheckpointTuple | None
```
Get a checkpoint tuple from the database.
This method retrieves a checkpoint tuple from the Postgres database based on the
provided config. If the config contains a "checkpoint\_id" key, the checkpoint with
the matching thread ID and "checkpoint\_id" is retrieved. Otherwise, the latest checkpoint
for the given thread ID is retrieved.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to use for retrieving the checkpoint. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `CheckpointTuple | None` | Optional[CheckpointTuple]: The retrieved checkpoint tuple, or None if no matching checkpoint was found. |
### put [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.put "Permanent link")
```
put(
    config: RunnableConfig,
    checkpoint: Checkpoint,
    metadata: CheckpointMetadata,
    new_versions: ChannelVersions,
) -> RunnableConfig
```
Save a checkpoint to the database.
This method saves a checkpoint to the Postgres database. The checkpoint is associated
with the provided config and its parent config (if any).
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | The config to associate with the checkpoint. | *required* |
| `checkpoint` | `Checkpoint` | The checkpoint to save. | *required* |
| `metadata` | `CheckpointMetadata` | Additional metadata to save with the checkpoint. | *required* |
| `new_versions` | `ChannelVersions` | New channel versions as of this write. | *required* |
Returns:
| Name | Type | Description |
| --- | --- | --- |
| `RunnableConfig` | `RunnableConfig` | Updated configuration after storing the checkpoint. |
### put\_writes [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.put_writes "Permanent link")
```
put_writes(
    config: RunnableConfig,
    writes: Sequence[tuple[str, Any]],
    task_id: str,
    task_path: str = "",
) -> None
```
Store intermediate writes linked to a checkpoint.
This method saves intermediate writes associated with a checkpoint to the database.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration of the related checkpoint. | *required* |
| `writes` | `Sequence[tuple[str, Any]]` | List of writes to store, each as (channel, value) pair. | *required* |
| `task_id` | `str` | Identifier for the task creating the writes. | *required* |
| `task_path` | `str` | Path of the task creating the writes. | `''` |
### delete\_thread [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.delete_thread "Permanent link")
```
delete_thread(thread_id: str) -> None
```
Delete all checkpoints and writes associated with a thread ID.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `thread_id` | `str` | The thread ID to delete. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `None` | None |
### get [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.get "Permanent link")
```
get(config: RunnableConfig) -> Checkpoint | None
```
Fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
### aget `async` [¶](#langgraph.checkpoint.postgres.aio.AsyncPostgresSaver.aget "Permanent link")
```
aget(config: RunnableConfig) -> Checkpoint | None
```
Asynchronously fetch a checkpoint using the given configuration.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `config` | `RunnableConfig` | Configuration specifying which checkpoint to retrieve. | *required* |
Returns:
| Type | Description |
| --- | --- |
| `Checkpoint | None` | Optional[Checkpoint]: The requested checkpoint, or None if not found. |
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/checkpoints/)
