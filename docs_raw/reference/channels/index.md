# Channels

# Channels[¶](#channels "Permanent link")
Classes:
| Name | Description |
| --- | --- |
| `BaseChannel` | Base class for all channels. |
## BaseChannel [¶](#langgraph.channels.base.BaseChannel "Permanent link")
Bases: `Generic[Value, Update, Checkpoint]`, `ABC`
Base class for all channels.
Methods:
| Name | Description |
| --- | --- |
| `copy` | Return a copy of the channel. |
| `checkpoint` | Return a serializable representation of the channel's current state. |
| `from_checkpoint` | Return a new identical channel, optionally initialized from a checkpoint. |
| `get` | Return the current value of the channel. |
| `is_available` | Return True if the channel is available (not empty), False otherwise. |
| `update` | Update the channel's value with the given sequence of updates. |
| `consume` | Notify the channel that a subscribed task ran. By default, no-op. |
| `finish` | Notify the channel that the Pregel run is finishing. By default, no-op. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `ValueType` | `Any` | The type of the value stored in the channel. |
| `UpdateType` | `Any` | The type of the update received by the channel. |
### ValueType `abstractmethod` `property` [¶](#langgraph.channels.base.BaseChannel.ValueType "Permanent link")
```
ValueType: Any
```
The type of the value stored in the channel.
### UpdateType `abstractmethod` `property` [¶](#langgraph.channels.base.BaseChannel.UpdateType "Permanent link")
```
UpdateType: Any
```
The type of the update received by the channel.
### copy [¶](#langgraph.channels.base.BaseChannel.copy "Permanent link")
```
copy() -> Self
```
Return a copy of the channel.
By default, delegates to checkpoint() and from\_checkpoint().
Subclasses can override this method with a more efficient implementation.
### checkpoint [¶](#langgraph.channels.base.BaseChannel.checkpoint "Permanent link")
```
checkpoint() -> Checkpoint | Any
```
Return a serializable representation of the channel's current state.
Raises EmptyChannelError if the channel is empty (never updated yet),
or doesn't support checkpoints.
### from\_checkpoint `abstractmethod` [¶](#langgraph.channels.base.BaseChannel.from_checkpoint "Permanent link")
```
from_checkpoint(checkpoint: Checkpoint | Any) -> Self
```
Return a new identical channel, optionally initialized from a checkpoint.
If the checkpoint contains complex data structures, they should be copied.
### get `abstractmethod` [¶](#langgraph.channels.base.BaseChannel.get "Permanent link")
```
get() -> Value
```
Return the current value of the channel.
Raises EmptyChannelError if the channel is empty (never updated yet).
### is\_available [¶](#langgraph.channels.base.BaseChannel.is_available "Permanent link")
```
is_available() -> bool
```
Return True if the channel is available (not empty), False otherwise.
Subclasses should override this method to provide a more efficient
implementation than calling get() and catching EmptyChannelError.
### update `abstractmethod` [¶](#langgraph.channels.base.BaseChannel.update "Permanent link")
```
update(values: Sequence[Update]) -> bool
```
Update the channel's value with the given sequence of updates.
The order of the updates in the sequence is arbitrary.
This method is called by Pregel for all channels at the end of each step.
If there are no updates, it is called with an empty sequence.
Raises InvalidUpdateError if the sequence of updates is invalid.
Returns True if the channel was updated, False otherwise.
### consume [¶](#langgraph.channels.base.BaseChannel.consume "Permanent link")
```
consume() -> bool
```
Notify the channel that a subscribed task ran. By default, no-op.
A channel can use this method to modify its state, preventing the value
from being consumed again.
Returns True if the channel was updated, False otherwise.
### finish [¶](#langgraph.channels.base.BaseChannel.finish "Permanent link")
```
finish() -> bool
```
Notify the channel that the Pregel run is finishing. By default, no-op.
A channel can use this method to modify its state, preventing finish.
Returns True if the channel was updated, False otherwise.
Classes:
| Name | Description |
| --- | --- |
| `Topic` | A configurable PubSub Topic. |
| `LastValue` | Stores the last value received, can receive at most one value per step. |
| `EphemeralValue` | Stores the value received in the step immediately preceding, clears after. |
| `BinaryOperatorAggregate` | Stores the result of applying a binary operator to the current value and each new value. |
| `AnyValue` | Stores the last value received, assumes that if multiple values are |
## Topic [¶](#langgraph.channels.Topic "Permanent link")
Bases: `Generic[Value]`, `BaseChannel[Sequence[Value], Union[Value, list[Value]], list[Value]]`
A configurable PubSub Topic.
Parameters:
| Name | Type | Description | Default |
| --- | --- | --- | --- |
| `typ` | `type[Value]` | The type of the value stored in the channel. | *required* |
| `accumulate` | `bool` | Whether to accumulate values across steps. If False, the channel will be emptied after each step. | `False` |
Methods:
| Name | Description |
| --- | --- |
| `consume` | Notify the channel that a subscribed task ran. By default, no-op. |
| `finish` | Notify the channel that the Pregel run is finishing. By default, no-op. |
| `copy` | Return a copy of the channel. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `ValueType` | `Any` | The type of the value stored in the channel. |
| `UpdateType` | `Any` | The type of the update received by the channel. |
### ValueType `property` [¶](#langgraph.channels.Topic.ValueType "Permanent link")
```
ValueType: Any
```
The type of the value stored in the channel.
### UpdateType `property` [¶](#langgraph.channels.Topic.UpdateType "Permanent link")
```
UpdateType: Any
```
The type of the update received by the channel.
### consume [¶](#langgraph.channels.Topic.consume "Permanent link")
```
consume() -> bool
```
Notify the channel that a subscribed task ran. By default, no-op.
A channel can use this method to modify its state, preventing the value
from being consumed again.
Returns True if the channel was updated, False otherwise.
### finish [¶](#langgraph.channels.Topic.finish "Permanent link")
```
finish() -> bool
```
Notify the channel that the Pregel run is finishing. By default, no-op.
A channel can use this method to modify its state, preventing finish.
Returns True if the channel was updated, False otherwise.
### copy [¶](#langgraph.channels.Topic.copy "Permanent link")
```
copy() -> Self
```
Return a copy of the channel.
## LastValue [¶](#langgraph.channels.LastValue "Permanent link")
Bases: `Generic[Value]`, `BaseChannel[Value, Value, Value]`
Stores the last value received, can receive at most one value per step.
Methods:
| Name | Description |
| --- | --- |
| `consume` | Notify the channel that a subscribed task ran. By default, no-op. |
| `finish` | Notify the channel that the Pregel run is finishing. By default, no-op. |
| `copy` | Return a copy of the channel. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `ValueType` | `type[Value]` | The type of the value stored in the channel. |
| `UpdateType` | `type[Value]` | The type of the update received by the channel. |
### ValueType `property` [¶](#langgraph.channels.LastValue.ValueType "Permanent link")
```
ValueType: type[Value]
```
The type of the value stored in the channel.
### UpdateType `property` [¶](#langgraph.channels.LastValue.UpdateType "Permanent link")
```
UpdateType: type[Value]
```
The type of the update received by the channel.
### consume [¶](#langgraph.channels.LastValue.consume "Permanent link")
```
consume() -> bool
```
Notify the channel that a subscribed task ran. By default, no-op.
A channel can use this method to modify its state, preventing the value
from being consumed again.
Returns True if the channel was updated, False otherwise.
### finish [¶](#langgraph.channels.LastValue.finish "Permanent link")
```
finish() -> bool
```
Notify the channel that the Pregel run is finishing. By default, no-op.
A channel can use this method to modify its state, preventing finish.
Returns True if the channel was updated, False otherwise.
### copy [¶](#langgraph.channels.LastValue.copy "Permanent link")
```
copy() -> Self
```
Return a copy of the channel.
## EphemeralValue [¶](#langgraph.channels.EphemeralValue "Permanent link")
Bases: `Generic[Value]`, `BaseChannel[Value, Value, Value]`
Stores the value received in the step immediately preceding, clears after.
Methods:
| Name | Description |
| --- | --- |
| `consume` | Notify the channel that a subscribed task ran. By default, no-op. |
| `finish` | Notify the channel that the Pregel run is finishing. By default, no-op. |
| `copy` | Return a copy of the channel. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `ValueType` | `type[Value]` | The type of the value stored in the channel. |
| `UpdateType` | `type[Value]` | The type of the update received by the channel. |
### ValueType `property` [¶](#langgraph.channels.EphemeralValue.ValueType "Permanent link")
```
ValueType: type[Value]
```
The type of the value stored in the channel.
### UpdateType `property` [¶](#langgraph.channels.EphemeralValue.UpdateType "Permanent link")
```
UpdateType: type[Value]
```
The type of the update received by the channel.
### consume [¶](#langgraph.channels.EphemeralValue.consume "Permanent link")
```
consume() -> bool
```
Notify the channel that a subscribed task ran. By default, no-op.
A channel can use this method to modify its state, preventing the value
from being consumed again.
Returns True if the channel was updated, False otherwise.
### finish [¶](#langgraph.channels.EphemeralValue.finish "Permanent link")
```
finish() -> bool
```
Notify the channel that the Pregel run is finishing. By default, no-op.
A channel can use this method to modify its state, preventing finish.
Returns True if the channel was updated, False otherwise.
### copy [¶](#langgraph.channels.EphemeralValue.copy "Permanent link")
```
copy() -> Self
```
Return a copy of the channel.
## BinaryOperatorAggregate [¶](#langgraph.channels.BinaryOperatorAggregate "Permanent link")
Bases: `Generic[Value]`, `BaseChannel[Value, Value, Value]`
Stores the result of applying a binary operator to the current value and each new value.
```
import operator
total = Channels.BinaryOperatorAggregate(int, operator.add)
```
Methods:
| Name | Description |
| --- | --- |
| `consume` | Notify the channel that a subscribed task ran. By default, no-op. |
| `finish` | Notify the channel that the Pregel run is finishing. By default, no-op. |
| `copy` | Return a copy of the channel. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `ValueType` | `type[Value]` | The type of the value stored in the channel. |
| `UpdateType` | `type[Value]` | The type of the update received by the channel. |
### ValueType `property` [¶](#langgraph.channels.BinaryOperatorAggregate.ValueType "Permanent link")
```
ValueType: type[Value]
```
The type of the value stored in the channel.
### UpdateType `property` [¶](#langgraph.channels.BinaryOperatorAggregate.UpdateType "Permanent link")
```
UpdateType: type[Value]
```
The type of the update received by the channel.
### consume [¶](#langgraph.channels.BinaryOperatorAggregate.consume "Permanent link")
```
consume() -> bool
```
Notify the channel that a subscribed task ran. By default, no-op.
A channel can use this method to modify its state, preventing the value
from being consumed again.
Returns True if the channel was updated, False otherwise.
### finish [¶](#langgraph.channels.BinaryOperatorAggregate.finish "Permanent link")
```
finish() -> bool
```
Notify the channel that the Pregel run is finishing. By default, no-op.
A channel can use this method to modify its state, preventing finish.
Returns True if the channel was updated, False otherwise.
### copy [¶](#langgraph.channels.BinaryOperatorAggregate.copy "Permanent link")
```
copy() -> Self
```
Return a copy of the channel.
## AnyValue [¶](#langgraph.channels.AnyValue "Permanent link")
Bases: `Generic[Value]`, `BaseChannel[Value, Value, Value]`
Stores the last value received, assumes that if multiple values are
received, they are all equal.
Methods:
| Name | Description |
| --- | --- |
| `consume` | Notify the channel that a subscribed task ran. By default, no-op. |
| `finish` | Notify the channel that the Pregel run is finishing. By default, no-op. |
| `copy` | Return a copy of the channel. |
Attributes:
| Name | Type | Description |
| --- | --- | --- |
| `ValueType` | `type[Value]` | The type of the value stored in the channel. |
| `UpdateType` | `type[Value]` | The type of the update received by the channel. |
### ValueType `property` [¶](#langgraph.channels.AnyValue.ValueType "Permanent link")
```
ValueType: type[Value]
```
The type of the value stored in the channel.
### UpdateType `property` [¶](#langgraph.channels.AnyValue.UpdateType "Permanent link")
```
UpdateType: type[Value]
```
The type of the update received by the channel.
### consume [¶](#langgraph.channels.AnyValue.consume "Permanent link")
```
consume() -> bool
```
Notify the channel that a subscribed task ran. By default, no-op.
A channel can use this method to modify its state, preventing the value
from being consumed again.
Returns True if the channel was updated, False otherwise.
### finish [¶](#langgraph.channels.AnyValue.finish "Permanent link")
```
finish() -> bool
```
Notify the channel that the Pregel run is finishing. By default, no-op.
A channel can use this method to modify its state, preventing finish.
Returns True if the channel was updated, False otherwise.
### copy [¶](#langgraph.channels.AnyValue.copy "Permanent link")
```
copy() -> Self
```
Return a copy of the channel.
Back to top

[Source](https://langchain-ai.github.io/langgraph/reference/channels/)
