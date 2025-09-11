# Caching

# Caching
## Caching[¶](#caching "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `BaseCache` | Base class for a cache. |
## BaseCache [¶](#langgraph.cache.base.BaseCache "Permanent link")
Bases: `ABC`, `Generic[ValueT]`
Base class for a cache.
Methods:
| Name | Description |
| --- | --- |
| `__init__` | Initialize the cache with a serializer. |
| `get` | Get the cached values for the given keys. |
| `aget` | Asynchronously get the cached values for the given keys. |
| `set` | Set the cached values for the given keys and TTLs. |
| `aset` | Asynchronously set the cached values for the given keys and TTLs. |
| `clear` | Delete the cached values for the given namespaces. |
| `aclear` | Asynchronously delete the cached values for the given namespaces. |
### \_\_init\_\_ [¶](#langgraph.cache.base.BaseCache.__init__ "Permanent link")
```
__init__(
    *, serde: SerializerProtocol | None = None
) -> None
```
Initialize the cache with a serializer.
### get `abstractmethod` [¶](#langgraph.cache.base.BaseCache.get "Permanent link")
```
get(keys: Sequence[FullKey]) -> dict[FullKey, ValueT]
```
Get the cached values for the given keys.
### aget `abstractmethod` `async` [¶](#langgraph.cache.base.BaseCache.aget "Permanent link")
```
aget(keys: Sequence[FullKey]) -> dict[FullKey, ValueT]
```
Asynchronously get the cached values for the given keys.
### set `abstractmethod` [¶](#langgraph.cache.base.BaseCache.set "Permanent link")
```
set(
    pairs: Mapping[FullKey, tuple[ValueT, int | None]],
) -> None
```
Set the cached values for the given keys and TTLs.
### aset `abstractmethod` `async` [¶](#langgraph.cache.base.BaseCache.aset "Permanent link")
```
aset(
    pairs: Mapping[FullKey, tuple[ValueT, int | None]],
) -> None
```
Asynchronously set the cached values for the given keys and TTLs.
### clear `abstractmethod` [¶](#langgraph.cache.base.BaseCache.clear "Permanent link")
```
clear(
    namespaces: Sequence[Namespace] | None = None,
) -> None
```
Delete the cached values for the given namespaces.
If no namespaces are provided, clear all cached values.
### aclear `abstractmethod` `async` [¶](#langgraph.cache.base.BaseCache.aclear "Permanent link")
```
aclear(
    namespaces: Sequence[Namespace] | None = None,
) -> None
```
Asynchronously delete the cached values for the given namespaces.
If no namespaces are provided, clear all cached values.
Classes:
| Name | Description |
| --- | --- |
| `InMemoryCache` |  |
## InMemoryCache [¶](#langgraph.cache.memory.InMemoryCache "Permanent link")
Bases: `BaseCache[ValueT]`
Methods:
| Name | Description |
| --- | --- |
| `get` | Get the cached values for the given keys. |
| `aget` | Asynchronously get the cached values for the given keys. |
| `set` | Set the cached values for the given keys. |
| `aset` | Asynchronously set the cached values for the given keys. |
| `clear` | Delete the cached values for the given namespaces. |
| `aclear` | Asynchronously delete the cached values for the given namespaces. |
### get [¶](#langgraph.cache.memory.InMemoryCache.get "Permanent link")
```
get(keys: Sequence[FullKey]) -> dict[FullKey, ValueT]
```
Get the cached values for the given keys.
### aget `async` [¶](#langgraph.cache.memory.InMemoryCache.aget "Permanent link")
```
aget(keys: Sequence[FullKey]) -> dict[FullKey, ValueT]
```
Asynchronously get the cached values for the given keys.
### set [¶](#langgraph.cache.memory.InMemoryCache.set "Permanent link")
```
set(
    keys: Mapping[FullKey, tuple[ValueT, int | None]],
) -> None
```
Set the cached values for the given keys.
### aset `async` [¶](#langgraph.cache.memory.InMemoryCache.aset "Permanent link")
```
aset(
    keys: Mapping[FullKey, tuple[ValueT, int | None]],
) -> None
```
Asynchronously set the cached values for the given keys.
### clear [¶](#langgraph.cache.memory.InMemoryCache.clear "Permanent link")
```
clear(
    namespaces: Sequence[Namespace] | None = None,
) -> None
```
Delete the cached values for the given namespaces.
If no namespaces are provided, clear all cached values.
### aclear `async` [¶](#langgraph.cache.memory.InMemoryCache.aclear "Permanent link")
```
aclear(
    namespaces: Sequence[Namespace] | None = None,
) -> None
```
Asynchronously delete the cached values for the given namespaces.
If no namespaces are provided, clear all cached values.
Classes:
| Name | Description |
| --- | --- |
| `SqliteCache` | File-based cache using SQLite. |
## SqliteCache [¶](#langgraph.cache.sqlite.SqliteCache "Permanent link")
Bases: `BaseCache[ValueT]`
File-based cache using SQLite.
Methods:
| Name | Description |
| --- | --- |
| `__init__` | Initialize the cache with a file path. |
| `get` | Get the cached values for the given keys. |
| `aget` | Asynchronously get the cached values for the given keys. |
| `set` | Set the cached values for the given keys and TTLs. |
| `aset` | Asynchronously set the cached values for the given keys and TTLs. |
| `clear` | Delete the cached values for the given namespaces. |
| `aclear` | Asynchronously delete the cached values for the given namespaces. |
### \_\_init\_\_ [¶](#langgraph.cache.sqlite.SqliteCache.__init__ "Permanent link")
```
__init__(
    *, path: str, serde: SerializerProtocol | None = None
) -> None
```
Initialize the cache with a file path.
### get [¶](#langgraph.cache.sqlite.SqliteCache.get "Permanent link")
```
get(keys: Sequence[FullKey]) -> dict[FullKey, ValueT]
```
Get the cached values for the given keys.
### aget `async` [¶](#langgraph.cache.sqlite.SqliteCache.aget "Permanent link")
```
aget(keys: Sequence[FullKey]) -> dict[FullKey, ValueT]
```
Asynchronously get the cached values for the given keys.
### set [¶](#langgraph.cache.sqlite.SqliteCache.set "Permanent link")
```
set(
    mapping: Mapping[FullKey, tuple[ValueT, int | None]],
) -> None
```
Set the cached values for the given keys and TTLs.
### aset `async` [¶](#langgraph.cache.sqlite.SqliteCache.aset "Permanent link")
```
aset(
    mapping: Mapping[FullKey, tuple[ValueT, int | None]],
) -> None
```
Asynchronously set the cached values for the given keys and TTLs.
### clear [¶](#langgraph.cache.sqlite.SqliteCache.clear "Permanent link")
```
clear(
    namespaces: Sequence[Namespace] | None = None,
) -> None
```
Delete the cached values for the given namespaces.
If no namespaces are provided, clear all cached values.
### aclear `async` [¶](#langgraph.cache.sqlite.SqliteCache.aclear "Permanent link")
```
aclear(
    namespaces: Sequence[Namespace] | None = None,
) -> None
```
Asynchronously delete the cached values for the given namespaces.
If no namespaces are provided, clear all cached values.
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/cache/)
