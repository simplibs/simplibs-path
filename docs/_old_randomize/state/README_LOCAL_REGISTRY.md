# 🔒 `LocalRegistry` — Isolated, Scoped Registry with Global Fallback

`LocalRegistry` is the second concrete class built on top of
[`RegistryBase`](README_REGISTRY_BASE.md). It exists to let you temporarily or locally
override randomizer behavior — inside a test, a specific code path, or a scoped
subsystem — **without mutating the global `RANDOMIZERS` singleton**.

Unlike an isolated `RandomizersRegistry()` instance, `LocalRegistry` is not fully
separate: it keeps read-only references to the global singleton's own dictionaries
(`_global_user_randomizers`, `_global_subclass_index`), so any global override is still
visible through it. Only *writes* are isolated. This produces a three-tier resolution
chain:

```
local_user  →  global_user  →  defaults
```

```python
class LocalRegistry(
    MappingDunders,      # locals variant
    MappingMethods,      # locals variant
    SubclassMethods,     # locals variant
    KeyCeckers,          # locals variant
    PublickHelpers,      # commons
    ContextualApi,       # commons
    RegistryBase[K, V],
):
    ...
```

For the shared `__enter__` / `__exit__` context-manager behavior, see
[`RegistryBase`](README_REGISTRY_BASE.md#__enter__).

```python
# Two equivalent usage patterns
with LocalRegistry() as reg:
    reg.add(MyType, my_randomizer)
    value = randomize(dict[str, MyType])   # module function, picks up active context

reg = LocalRegistry()
reg.add(MyType, my_randomizer)
value = reg.randomize(dict[str, MyType])   # instance method, manages `with` internally
```

---

## 🧭 Table of Contents

### Internal State
* [`__init__`](#__init__)
* [`_global_user_randomizers`](#_global_user_randomizers)
* [`_global_subclass_index`](#_global_subclass_index)
* [`__repr__`](#__repr__)

### Mapping Dunders
* [`__setitem__`](#__setitem__)
* [`__delitem__`](#__delitem__)
* [`__getitem__`](#__getitem__)
* [`__contains__`](#__contains__)
* [`__iter__`](#__iter__)
* [`__len__`](#__len__)

### Mapping Methods
* [`clear`](#clear)
* [`pop`](#pop)

### Subclass Resolution
* [`has_subclasses`](#has_subclasses)
* [`subclass_search`](#subclass_search)

### Key Verification & Introspection
* [`get_default_keys`](#get_default_keys)
* [`get_global_users_keys`](#get_global_users_keys)
* [`get_global_subclass_keys`](#get_global_subclass_keys)
* [`get_local_users_keys`](#get_local_users_keys)
* [`get_local_subclass_keys`](#get_local_subclass_keys)
* [`has_global_user_override`](#has_global_user_override)
* [`has_local_user_override`](#has_local_user_override)
* [`get_keys_overview`](#get_keys_overview)

### Public Helper Interface
* [`add`](#add)
* [`add_many`](#add_many)
* [`remove`](#remove)
* [`remove_many`](#remove_many)
* [`reset`](#reset)

### Contextual API
* [`get_randomizer`](#get_randomizer)
* [`randomize`](#randomize)
* [`bulk_randomizer`](#bulk_randomizer)

### Context Manager Protocol
* `__enter__` / `__exit__` — inherited unchanged, see
  [`RegistryBase`](README_REGISTRY_BASE.md#__enter__)

---

## Internal State

### `__init__`

Initializes the local registry. Links two read-only properties to the global singleton's
internal dictionaries (`_user_randomizers`, `_subclass_index` of `RANDOMIZERS`), then
creates two brand-new, empty dictionaries for local-only storage.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
from simplibs.randomize.registry.classes import LocalRegistry

local_reg = LocalRegistry()
```

**Under the hood:**
```python
def __init__(self) -> None:
    super().__init__()
    from ..RANDOMIZERS import RANDOMIZERS
    self.__global_user_randomizers: dict = RANDOMIZERS._user_randomizers
    self.__global_subclass_index: dict = RANDOMIZERS._subclass_index
    self._local_user_randomizers: dict = {}
    self._local_subclass_index: dict = {}
```

[▲ Back to top](#-table-of-contents)

---

### `_global_user_randomizers`

Read-only property exposing the *linked* global user-override dictionary (the same
object owned by `RANDOMIZERS._user_randomizers`, not a copy).

**Parameters:**
* *(none — property getter)*

**Returns:**
* `dict`: The linked global user-override mapping.

**Example usage:**
```python
local_reg = LocalRegistry()
print(local_reg._global_user_randomizers)  # mirrors RANDOMIZERS._user_randomizers
```

**Under the hood:**
```python
@property
def _global_user_randomizers(self) -> dict:
    return self.__global_user_randomizers
```

[▲ Back to top](#-table-of-contents)

---

### `_global_subclass_index`

Read-only property exposing the *linked* global subclass index (again, the same object
owned by `RANDOMIZERS._subclass_index`).

**Parameters:**
* *(none — property getter)*

**Returns:**
* `dict`: The linked global subclass-index mapping.

**Example usage:**
```python
local_reg = LocalRegistry()
print(local_reg._global_subclass_index)
```

**Under the hood:**
```python
@property
def _global_subclass_index(self) -> dict:
    return self.__global_subclass_index
```

[▲ Back to top](#-table-of-contents)

---

### `__repr__`

Returns a concise, human-readable summary of both the local and the linked global
registry state — useful for confirming exactly what a local override chain currently
sees.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `str`: A summary string with local/global override and subclass counts, plus the
  default count.

**Example usage:**
```python
print(repr(local_reg))
# LocalRegistry(local_overrides=1, local_subclasses=0, global_overrides=2, global_subclasses=1, defaults_count=19)
```

**Under the hood:**
```python
def __repr__(self) -> str:
    return (
        f"{type(self).__name__}("
        f"local_overrides={len(self._local_user_randomizers)}, "
        f"local_subclasses={len(self._local_subclass_index)}, "
        f"global_overrides={len(self._global_user_randomizers)}, "
        f"global_subclasses={len(self._global_subclass_index)}, "
        f"defaults_count={len(self._default_randomizers)}"
        f")"
    )
```

[▲ Back to top](#-table-of-contents)

---

## Mapping Dunders

### `__setitem__`

Registers a randomizer callable under a given key, after validation, into **local
storage only**. Never touches the global dictionaries.

**Parameters:**
* `key` (*K*): Data type or lookup key to register under.
* `value` (*V*): Generator callable.

**Returns:**
* `None`

**Raises:**
* `ValueError`: If the key is `None` or the value is not callable.

**Example usage:**
```python
local_reg[str] = lambda: "LOCAL_OVERRIDE"
```

**Under the hood:**
```python
def __setitem__(self, key: K, value: V) -> None:
    if key is None or not callable(value):
        validate_key_is_none(key)
        validate_value_is_not_callable(key, value)

    self._local_user_randomizers[key] = value
    if isinstance(key, type):
        self._local_subclass_index[key] = value
```

[▲ Back to top](#-table-of-contents)

---

### `__delitem__`

Removes a local override for the given key. Cannot remove global or default entries this
way — attempting to do so raises a dedicated error indicating which layer actually owns
the key.

**Parameters:**
* `key` (*K*): Target key to remove.

**Returns:**
* `None`

**Raises:**
* `KeyError`: If the key isn't a local override (with a distinct message depending on
  whether it belongs to globals or defaults).

**Example usage:**
```python
del local_reg[str]
```

**Under the hood:**
```python
def __delitem__(self, key: K) -> None:
    if key not in self._local_user_randomizers:
        validate_key_is_from_globals(key)
        validate_key_is_from_defaults(key)
        raise_key_not_found(key)

    self._local_user_randomizers.pop(key, None)
    self._local_subclass_index.pop(key, None)
```

[▲ Back to top](#-table-of-contents)

---

### `__getitem__`

Resolves a randomizer callable through the full three-tier chain: local overrides first,
then global overrides, then built-in defaults.

**Parameters:**
* `key` (*K*): Target key to look up.

**Returns:**
* `V`: The resolved randomizer callable.

**Raises:**
* `KeyError`: If the key isn't found in any of the three tiers.

**Example usage:**
```python
value_generator = local_reg[int]
```

**Under the hood:**
```python
def __getitem__(self, key: K) -> V:
    if key in self._local_user_randomizers:
        return self._local_user_randomizers[key]
    if key in self._global_user_randomizers:
        return self._global_user_randomizers[key]
    if key in self._default_randomizers:
        return self._default_randomizers[key]
    raise_key_not_found(key)
    return None
```

[▲ Back to top](#-table-of-contents)

---

### `__contains__`

Checks whether a key resolves anywhere across the three tiers.

**Parameters:**
* `key` (*object*): Key to test.

**Returns:**
* `bool`: `True` if resolvable locally, globally, or as a default.

**Example usage:**
```python
if str in local_reg:
    ...
```

**Under the hood:**
```python
def __contains__(self, key: object) -> bool:
    return (
        key in self._local_user_randomizers
        or key in self._global_user_randomizers
        or key in self._default_randomizers
    )
```

[▲ Back to top](#-table-of-contents)

---

### `__iter__`

Yields every resolvable key exactly once, in precedence order: local, then global, then
defaults.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `Iterator[K]`: An iterator over all deduplicated keys.

**Example usage:**
```python
for key in local_reg:
    print(key)
```

**Under the hood:**
```python
def __iter__(self) -> Iterator[K]:
    seen: set[K] = set()
    for key in self._local_user_randomizers:
        seen.add(key)
        yield key

    for key in self._global_user_randomizers:
        if key not in seen:
            seen.add(key)
            yield key

    for key in self._default_randomizers:
        if key not in seen:
            seen.add(key)
            yield key
```

[▲ Back to top](#-table-of-contents)

---

### `__len__`

Returns the total number of distinct, resolvable keys across all three tiers.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `int`: Count of deduplicated keys.

**Example usage:**
```python
print(len(local_reg))
```

**Under the hood:**
```python
def __len__(self) -> int:
    return len(
        set(self._local_user_randomizers) |
        set(self._global_user_randomizers) |
        set(self._default_randomizers)
    )
```

[▲ Back to top](#-table-of-contents)

---

## Mapping Methods

### `clear`

Removes all **local** overrides only. Global overrides and built-in defaults are left
completely untouched.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
local_reg.clear()
```

**Under the hood:**
```python
def clear(self) -> None:
    self._local_user_randomizers.clear()
    self._local_subclass_index.clear()
```

[▲ Back to top](#-table-of-contents)

---

### `pop`

Removes a local override and returns its value, with optional default fallback — same
`UNSET`-sentinel contract as `RandomizersRegistry.pop`.

**Parameters:**
* `key` (*K*): Target key to pop.
* `default` (*Any*, optional): Fallback value if the key is missing locally. Defaults to
  `UNSET`.

**Returns:**
* `V`: The removed randomizer, or `default`.

**Raises:**
* `KeyError`: If the key is missing and no `default` was provided.

**Example usage:**
```python
local_reg.pop(str, None)
```

**Under the hood:**
```python
def pop(self, key: K, default: Any = UNSET) -> V:
    try:
        value = self[key]
        del self[key]
        return value
    except KeyError:
        if default is UNSET:
            raise_pop_key_not_found(key)
        return default
```

[▲ Back to top](#-table-of-contents)

---

## Subclass Resolution

### `has_subclasses`

Reports whether any subclass mappings are registered — locally **or** globally.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `bool`: `True` if either `_local_subclass_index` or `_global_subclass_index` is
  non-empty.

**Example usage:**
```python
if local_reg.has_subclasses():
    ...
```

**Under the hood:**
```python
def has_subclasses(self) -> bool:
    return (
        bool(self._local_subclass_index)
        or bool(self._global_subclass_index)
    )
```

[▲ Back to top](#-table-of-contents)

---

### `subclass_search`

Performs a two-stage `issubclass()` scan: local subclass index first, then global
subclass index — local definitions always take precedence.

**Parameters:**
* `value_type` (*Any*): Target class to check against registered base classes.

**Returns:**
* `V | None`: The matching randomizer, or `None` if `value_type` isn't a class or no
  base class matches in either layer.

**Example usage:**
```python
class Money(Decimal):
    pass

randomizer = local_reg.subclass_search(Money)
```

**Under the hood:**
```python
def subclass_search(self, value_type: Any) -> V | None:
    if not isinstance(value_type, type):
        return None

    # Local subclasses search
    for base_type, randomizer in self._local_subclass_index.items():
        if issubclass(value_type, base_type):
            return randomizer

    # Global subclasses search
    for base_type, randomizer in self._global_subclass_index.items():
        if issubclass(value_type, base_type):
            return randomizer

    return None
```

[▲ Back to top](#-table-of-contents)

---

## Key Verification & Introspection

### `get_default_keys`

Returns all built-in default randomizer keys.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All default keys.

**Example usage:**
```python
print(local_reg.get_default_keys())
```

**Under the hood:**
```python
def get_default_keys(self) -> tuple[Any, ...]:
    return tuple(self._default_randomizers.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `get_global_users_keys`

Returns all keys explicitly overridden in the **global** registry (as seen through this
local instance).

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All global user-override keys.

**Example usage:**
```python
print(local_reg.get_global_users_keys())
```

**Under the hood:**
```python
def get_global_users_keys(self) -> tuple[Any, ...]:
    return tuple(self._global_user_randomizers.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `get_global_subclass_keys`

Returns all keys registered for subclass matching in the **global** registry.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All global subclass-index keys.

**Example usage:**
```python
print(local_reg.get_global_subclass_keys())
```

**Under the hood:**
```python
def get_global_subclass_keys(self) -> tuple[Any, ...]:
    return tuple(self._global_subclass_index.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `get_local_users_keys`

Returns all keys explicitly overridden **locally**.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All local user-override keys.

**Example usage:**
```python
print(local_reg.get_local_users_keys())
```

**Under the hood:**
```python
def get_local_users_keys(self) -> tuple[Any, ...]:
    return tuple(self._local_user_randomizers.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `get_local_subclass_keys`

Returns all keys registered for subclass matching **locally**.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All local subclass-index keys.

**Example usage:**
```python
print(local_reg.get_local_subclass_keys())
```

**Under the hood:**
```python
def get_local_subclass_keys(self) -> tuple[Any, ...]:
    return tuple(self._local_subclass_index.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `has_global_user_override`

Checks whether a specific key has an explicit override in the **global** registry.

**Parameters:**
* `key` (*K*): Key to check.

**Returns:**
* `bool`: `True` if a global user override exists.

**Example usage:**
```python
if local_reg.has_global_user_override(str):
    ...
```

**Under the hood:**
```python
def has_global_user_override(self, key: K) -> bool:
    return key in self._global_user_randomizers
```

[▲ Back to top](#-table-of-contents)

---

### `has_local_user_override`

Checks whether a specific key has an explicit override **locally**.

**Parameters:**
* `key` (*K*): Key to check.

**Returns:**
* `bool`: `True` if a local user override exists.

**Example usage:**
```python
if local_reg.has_local_user_override(str):
    ...
```

**Under the hood:**
```python
def has_local_user_override(self, key: K) -> bool:
    return key in self._local_user_randomizers
```

[▲ Back to top](#-table-of-contents)

---

### `get_keys_overview`

Returns a single dictionary summarizing all five storage layers at once (local
overrides, local subclasses, global overrides, global subclasses, defaults).

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `dict[str, tuple[Any, ...]]`: A dictionary with `"local_user_overrides"`,
  `"local_subclass_index"`, `"global_user_overrides"`, `"global_subclass_index"`, and
  `"defaults"` keys.

**Example usage:**
```python
overview = local_reg.get_keys_overview()
print(overview["local_user_overrides"])
```

**Under the hood:**
```python
def get_keys_overview(self) -> dict[str, tuple[Any, ...]]:
    return {
        "local_user_overrides": tuple(self._local_user_randomizers.keys()),
        "local_subclass_index": tuple(self._local_subclass_index.keys()),
        "global_user_overrides": tuple(self._global_user_randomizers.keys()),
        "global_subclass_index": tuple(self._global_subclass_index.keys()),
        "defaults": tuple(self._default_randomizers.keys()),
    }
```

[▲ Back to top](#-table-of-contents)

---

## Public Helper Interface

*(Identical in implementation to `RandomizersRegistry` — shared via the
`commons/PublickHelpers` mixin. Listed here for completeness since they're part of this
class's public surface too.)*

### `add`

Ergonomic alias for `registry[key] = value` — registers a single randomizer **locally**.

**Parameters:**
* `key` (*K*): Data type or lookup key to register under.
* `value` (*V*): Generator callable.

**Returns:**
* `None`

**Example usage:**
```python
local_reg.add(str, lambda: "LOCAL_OVERRIDE")
```

**Under the hood:**
```python
def add(self, key: K, value: V) -> None:
    self[key] = value
```

[▲ Back to top](#-table-of-contents)

---

### `add_many`

Registers multiple randomizers at once, locally, from a mapping.

**Parameters:**
* `mapping` (*Mapping[K, V]*): Dictionary of `(key, generator)` pairs.

**Returns:**
* `None`

**Example usage:**
```python
local_reg.add_many({str: lambda: "a", int: lambda: 1})
```

**Under the hood:**
```python
def add_many(self, mapping: Mapping[K, V]) -> None:
    self.update(mapping)
```

[▲ Back to top](#-table-of-contents)

---

### `remove`

Removes a local key and safely returns its randomizer, or `None` if not present locally
(never raises).

**Parameters:**
* `key` (*K*): Key to remove.

**Returns:**
* `V | None`: The removed randomizer, or `None`.

**Example usage:**
```python
local_reg.remove(str)
```

**Under the hood:**
```python
def remove(self, key: K) -> V | None:
    return self.pop(key, None)
```

[▲ Back to top](#-table-of-contents)

---

### `remove_many`

Removes multiple local keys in one call, silently skipping any that aren't locally
registered.

**Parameters:**
* `keys` (*Iterable[K]*): Keys to remove.

**Returns:**
* `None`

**Example usage:**
```python
local_reg.remove_many([str, int, bool])
```

**Under the hood:**
```python
def remove_many(self, keys: Iterable[K]) -> None:
    for key in keys:
        self.pop(key, None)
```

[▲ Back to top](#-table-of-contents)

---

### `reset`

Wipes all **local** overrides back to a clean state — alias for `clear()`. Global state
is unaffected.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
local_reg.reset()
```

**Under the hood:**
```python
def reset(self) -> None:
    self.clear()
```

[▲ Back to top](#-table-of-contents)

---

## Contextual API

*(Also shared via the `commons/ContextualApi` mixin — identical implementation to
`RandomizersRegistry`, but here `with self:` activates the local registry's three-tier
resolution chain instead of the global singleton.)*

### `get_randomizer`

Instance-bound equivalent of the module-level `get_randomizer()`, executed within this
local registry's own context.

**Parameters:**
* `value_type` (*Any*, optional): Type hint, class, or object to resolve a randomizer
  for. Defaults to `None`.

**Returns:**
* `Any`: The resolved generator callable, or `None`.

**Example usage:**
```python
local_reg.add(int, lambda: 42)
randomizer = local_reg.get_randomizer(int)
```

**Under the hood:**
```python
def get_randomizer(self, value_type: Any = None) -> Any:
    from .....get_randomizer import get_randomizer
    with self:
        return get_randomizer(value_type)
```

[▲ Back to top](#-table-of-contents)

---

### `randomize`

Instance-bound equivalent of the module-level `randomize()`, executed within this local
registry's own context.

**Parameters:**
* `value_type` (*Any*, optional): Target type hint. Defaults to `None`.
* `**kwargs` (*Any*): Extra keyword parameters forwarded to the resolved randomizer.

**Returns:**
* `Any`: The generated random value, or `None`.

**Raises:**
* `RandomizerNotFoundError`: If no matching randomizer could be resolved.
* `RandomizerExecutionFailedError`: If randomizer execution fails unexpectedly.

**Example usage:**
```python
local_reg = LocalRegistry()
local_reg.add(str, lambda: "TEST_OVERRIDE")

val_str = local_reg.randomize(str)  # -> "TEST_OVERRIDE"
```

**Under the hood:**
```python
def randomize(self, value_type: Any = None, **kwargs: Any) -> Any:
    from .....randomize import randomize
    with self:
        return randomize(value_type, **kwargs)
```

[▲ Back to top](#-table-of-contents)

---

### `bulk_randomizer`

Instance-bound equivalent of the module-level `bulk_randomizer()`, executed within this
local registry's own context.

**Parameters:**
* `*items` (*Any*): One or more target specifications — each a type hint, or a
  `(value_type, kwargs_mapping)` tuple. A single dict argument returns results keyed the
  same way.
* `get_randomizers` (*bool*, optional): If `True`, returns resolved callables instead of
  generated values. Defaults to `False`.

**Returns:**
* `Any`: A tuple of generated values/randomizers, or a dictionary if a single dict was
  passed.

**Example usage:**
```python
results = local_reg.bulk_randomizer(int, str, bool)
```

**Under the hood:**
```python
def bulk_randomizer(self, *items: Any, get_randomizers: bool = False) -> Any:
    from .....bulk_randomizer import bulk_randomizer
    with self:
        return bulk_randomizer(*items, get_randomizers=get_randomizers)
```

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../_README.md)