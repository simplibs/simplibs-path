# 🗂️ `RandomizersRegistry` — Global & Standalone Registry

`RandomizersRegistry` is the concrete, ready-to-use registry class built on top of
[`RegistryBase`](README_REGISTRY_BASE.md). It serves two purposes:

1. **The global singleton.** A single instance of this class (`RANDOMIZERS`) is created
   once and used as the system-wide default registry — this is what every randomizer
   falls back to unless a local override is active.


2. **A standalone registry class.** Because it's a normal class, you're free to
   instantiate `RandomizersRegistry()` yourself to build a completely isolated registry
   — for example in tests, where you want a clean environment with none of the global
   user overrides applied, or as a fully separate registry for a specific subsystem.

It resolves lookups across exactly two layers: **user overrides** (`_user_randomizers`),
then **built-in defaults** (`_default_randomizers`, inherited from `RegistryBase`).

```python
class RandomizersRegistry(
    MappingDunders,      # globals variant
    MappingMethods,      # globals variant
    SubclassMethods,     # globals variant
    KeyCeckers,          # globals variant
    PublickHelpers,      # commons
    ContextualApi,       # commons
    RegistryBase[K, V],
):
    ...
```

For the shared `__enter__` / `__exit__` context-manager behavior, see
[`RegistryBase`](README_REGISTRY_BASE.md#__enter__).

---

## 🧭 Table of Contents

### Internal State
* [`__init__`](#__init__)
* [`_user_randomizers`](#_user_randomizers)
* [`_subclass_index`](#_subclass_index)
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
* [`get_users_keys`](#get_users_keys)
* [`get_subclass_keys`](#get_subclass_keys)
* [`has_user_override`](#has_user_override)
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

Initializes the registry with two empty dictionaries: one for user-registered overrides,
one for the subclass (inheritance-based) index.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
from simplibs.randomize.registry.classes import RandomizersRegistry

# Building a completely isolated registry, e.g. for a test
test_registry = RandomizersRegistry()
```

**Under the hood:**
```python
def __init__(self) -> None:
    super().__init__()
    self.__user_randomizers: dict[K, V] = {}
    self.__subclass_index: dict[K, V] = {}
```

[▲ Back to top](#-table-of-contents)

---

### `_user_randomizers`

Read-only property exposing the internal dictionary of explicit user-registered
randomizers (exact-type matches only, no inheritance).

**Parameters:**
* *(none — property getter)*

**Returns:**
* `dict`: The internal user-override mapping.

**Example usage:**
```python
RANDOMIZERS.add(str, lambda: "TEST")
print(RANDOMIZERS._user_randomizers)  # {<class 'str'>: <function ...>}
```

**Under the hood:**
```python
@property
def _user_randomizers(self) -> dict:
    return self.__user_randomizers
```

[▲ Back to top](#-table-of-contents)

---

### `_subclass_index`

Read-only property exposing the internal dictionary used for inheritance-aware
(`issubclass`) lookups. Populated automatically whenever a registered key is itself a
class.

**Parameters:**
* *(none — property getter)*

**Returns:**
* `dict`: The internal subclass-index mapping.

**Example usage:**
```python
class Money(Decimal):
    pass

RANDOMIZERS.add(Money, lambda: Money("9.99"))
print(RANDOMIZERS._subclass_index)  # {<class 'Money'>: <function ...>}
```

**Under the hood:**
```python
@property
def _subclass_index(self) -> dict:
    return self.__subclass_index
```

[▲ Back to top](#-table-of-contents)

---

### `__repr__`

Returns a concise, human-readable summary of the registry's current state — useful for
debugging and logging.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `str`: A summary string showing counts of overrides, subclasses, and defaults.

**Example usage:**
```python
print(repr(RANDOMIZERS))
# RandomizersRegistry(own_overrides=2, subclasses=1, defaults_count=19)
```

**Under the hood:**
```python
def __repr__(self) -> str:
    return (
        f"{type(self).__name__}("
        f"own_overrides={len(self._user_randomizers)}, "
        f"subclasses={len(self._subclass_index)}, "
        f"defaults_count={len(self._default_randomizers)}"
        f")"
    )
```

[▲ Back to top](#-table-of-contents)

---

## Mapping Dunders

### `__setitem__`

Registers a randomizer callable under a given key, after validating that the key is not
`None` and the value is callable. If the key is a class, it's automatically indexed into
`_subclass_index` too.

**Parameters:**
* `key` (*K*): Data type or lookup key to register under.
* `value` (*V*): Generator callable for randomizing values.

**Returns:**
* `None`

**Raises:**
* `ValueError`: If the key is `None` or the value is not callable.

**Example usage:**
```python
RANDOMIZERS[str] = lambda: "custom-value"
```

**Under the hood:**
```python
def __setitem__(self, key: K, value: V) -> None:
    if key is None or not callable(value):
        validate_key_is_none(key)
        validate_value_is_not_callable(key, value)

    self._user_randomizers[key] = value
    if isinstance(key, type):
        self._subclass_index[key] = value
```

[▲ Back to top](#-table-of-contents)

---

### `__delitem__`

Removes a previously registered user override for the given key.

**Parameters:**
* `key` (*K*): Target key to remove.

**Returns:**
* `None`

**Raises:**
* `KeyError`: If the key is not present among user overrides (including a dedicated
  message if it's actually a built-in default and therefore cannot be removed this way).

**Example usage:**
```python
del RANDOMIZERS[str]
```

**Under the hood:**
```python
def __delitem__(self, key: K) -> None:
    if key not in self._user_randomizers:
        validate_key_is_from_defaults(key)
        raise_key_not_found(key)

    self._user_randomizers.pop(key, None)
    self._subclass_index.pop(key, None)
```

[▲ Back to top](#-table-of-contents)

---

### `__getitem__`

Resolves and returns the randomizer callable for a given key, checking user overrides
first, then falling back to built-in defaults.

**Parameters:**
* `key` (*K*): Target key to look up.

**Returns:**
* `V`: The resolved randomizer callable.

**Raises:**
* `KeyError`: If the key exists in neither user overrides nor defaults.

**Example usage:**
```python
int_randomizer = RANDOMIZERS[int]
value = int_randomizer()
```

**Under the hood:**
```python
def __getitem__(self, key: K) -> V:
    if key in self._user_randomizers:
        return self._user_randomizers[key]
    if key in self._default_randomizers:
        return self._default_randomizers[key]
    raise_key_not_found(key)
    return None
```

[▲ Back to top](#-table-of-contents)

---

### `__contains__`

Checks whether a key resolves to a randomizer, in either the user-override layer or the
built-in defaults layer.

**Parameters:**
* `key` (*object*): Key to test.

**Returns:**
* `bool`: `True` if the key is resolvable, `False` otherwise.

**Example usage:**
```python
if str in RANDOMIZERS:
    print("str is resolvable")
```

**Under the hood:**
```python
def __contains__(self, key: object) -> bool:
    return (
        key in self._user_randomizers
        or key in self._default_randomizers
    )
```

[▲ Back to top](#-table-of-contents)

---

### `__iter__`

Yields every resolvable key exactly once, prioritizing user overrides before defaults.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `Iterator[K]`: An iterator over all deduplicated keys.

**Example usage:**
```python
for key in RANDOMIZERS:
    print(key)
```

**Under the hood:**
```python
def __iter__(self) -> Iterator[K]:
    seen: set[K] = set()
    for key in self._user_randomizers:
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

Returns the total number of distinct, resolvable keys across user overrides and
defaults.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `int`: Count of deduplicated keys.

**Example usage:**
```python
print(len(RANDOMIZERS))
```

**Under the hood:**
```python
def __len__(self) -> int:
    return len(
        set(self._user_randomizers) |
        set(self._default_randomizers)
    )
```

[▲ Back to top](#-table-of-contents)

---

## Mapping Methods

### `clear`

Removes all user overrides (and their subclass index entries). Built-in defaults are
left completely untouched.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
RANDOMIZERS.clear()  # wipes all custom overrides, defaults remain intact
```

**Under the hood:**
```python
def clear(self) -> None:
    self._user_randomizers.clear()
    self._subclass_index.clear()
```

[▲ Back to top](#-table-of-contents)

---

### `pop`

Removes a user override and returns its value, with optional default fallback —
mirroring the built-in `dict.pop()` contract, including sentinel-based detection of "no
default provided."

**Parameters:**
* `key` (*K*): Target key to pop.
* `default` (*Any*, optional): Fallback value if the key is missing. Defaults to the
  internal `UNSET` sentinel.

**Returns:**
* `V`: The associated randomizer callable, or `default` if provided and the key was
  missing.

**Raises:**
* `KeyError`: If the key is missing and no `default` was provided.

**Example usage:**
```python
randomizer = RANDOMIZERS.pop(str, None)
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

Concrete implementation of the abstract `RegistryBase.has_subclasses`. Reports whether
any inheritance-based mappings exist.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `bool`: `True` if `_subclass_index` is non-empty.

**Example usage:**
```python
if RANDOMIZERS.has_subclasses():
    ...
```

**Under the hood:**
```python
def has_subclasses(self) -> bool:
    return bool(self._subclass_index)
```

[▲ Back to top](#-table-of-contents)

---

### `subclass_search`

Concrete implementation of the abstract `RegistryBase.subclass_search`. Performs a
linear `issubclass()` scan over `_subclass_index` and returns the first matching
randomizer.

**Parameters:**
* `value_type` (*Any*): Target class to check against registered base classes.

**Returns:**
* `V | None`: The matching randomizer, or `None` if `value_type` isn't a class or no
  base class matches.

**Example usage:**
```python
class Money(Decimal):
    pass

randomizer = RANDOMIZERS.subclass_search(Money)
```

**Under the hood:**
```python
def subclass_search(self, value_type: Any) -> V | None:
    if not isinstance(value_type, type):
        return None

    for base_type, randomizer in self._subclass_index.items():
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
print(RANDOMIZERS.get_default_keys())
```

**Under the hood:**
```python
def get_default_keys(self) -> tuple[Any, ...]:
    return tuple(self._default_randomizers.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `get_users_keys`

Returns all keys explicitly overridden by the user.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All user-override keys.

**Example usage:**
```python
print(RANDOMIZERS.get_users_keys())
```

**Under the hood:**
```python
def get_users_keys(self) -> tuple[Any, ...]:
    return tuple(self._user_randomizers.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `get_subclass_keys`

Returns all keys registered for subclass (inheritance) matching.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `tuple[Any, ...]`: All subclass-index keys.

**Example usage:**
```python
print(RANDOMIZERS.get_subclass_keys())
```

**Under the hood:**
```python
def get_subclass_keys(self) -> tuple[Any, ...]:
    return tuple(self._subclass_index.keys())
```

[▲ Back to top](#-table-of-contents)

---

### `has_user_override`

Checks whether a specific key has an explicit user override registered.

**Parameters:**
* `key` (*K*): Key to check.

**Returns:**
* `bool`: `True` if a user override exists for this key.

**Example usage:**
```python
if RANDOMIZERS.has_user_override(str):
    ...
```

**Under the hood:**
```python
def has_user_override(self, key: K) -> bool:
    return key in self._user_randomizers
```

[▲ Back to top](#-table-of-contents)

---

### `get_keys_overview`

Returns a single dictionary summarizing all storage layers at once — useful for
debugging/inspection in one call.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `dict[str, tuple[Any, ...]]`: A dictionary with `"user_overrides"`,
  `"subclass_index"`, and `"defaults"` keys.

**Example usage:**
```python
overview = RANDOMIZERS.get_keys_overview()
print(overview["user_overrides"])
```

**Under the hood:**
```python
def get_keys_overview(self) -> dict[str, tuple[Any, ...]]:
    return {
        "user_overrides": tuple(self._user_randomizers.keys()),
        "subclass_index": tuple(self._subclass_index.keys()),
        "defaults": tuple(self._default_randomizers.keys()),
    }
```

[▲ Back to top](#-table-of-contents)

---

## Public Helper Interface

### `add`

Ergonomic alias for `registry[key] = value` — registers a single randomizer.

**Parameters:**
* `key` (*K*): Data type or lookup key to register under.
* `value` (*V*): Generator callable.

**Returns:**
* `None`

**Example usage:**
```python
RANDOMIZERS.add(str, lambda: "custom-value")
```

**Under the hood:**
```python
def add(self, key: K, value: V) -> None:
    self[key] = value
```

[▲ Back to top](#-table-of-contents)

---

### `add_many`

Registers multiple randomizers at once from a mapping — a thin wrapper over the
inherited `MutableMapping.update()`.

**Parameters:**
* `mapping` (*Mapping[K, V]*): Dictionary of `(key, generator)` pairs.

**Returns:**
* `None`

**Example usage:**
```python
RANDOMIZERS.add_many({
    str: lambda: "a",
    int: lambda: 1,
})
```

**Under the hood:**
```python
def add_many(self, mapping: Mapping[K, V]) -> None:
    self.update(mapping)
```

[▲ Back to top](#-table-of-contents)

---

### `remove`

Removes a key and safely returns its randomizer, or `None` if it wasn't registered
(never raises).

**Parameters:**
* `key` (*K*): Key to remove.

**Returns:**
* `V | None`: The removed randomizer, or `None`.

**Example usage:**
```python
RANDOMIZERS.remove(str)
```

**Under the hood:**
```python
def remove(self, key: K) -> V | None:
    return self.pop(key, None)
```

[▲ Back to top](#-table-of-contents)

---

### `remove_many`

Removes multiple keys in one call, silently skipping any that aren't registered.

**Parameters:**
* `keys` (*Iterable[K]*): Keys to remove.

**Returns:**
* `None`

**Example usage:**
```python
RANDOMIZERS.remove_many([str, int, bool])
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

Wipes the entire registry back to a clean state — alias for `clear()`.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
RANDOMIZERS.reset()
```

**Under the hood:**
```python
def reset(self) -> None:
    self.clear()
```

[▲ Back to top](#-table-of-contents)

---

## Contextual API

### `get_randomizer`

Instance-bound equivalent of the module-level `get_randomizer()` function, executed
within this registry's own context (`with self:`), so lookups resolve against *this*
instance rather than whatever is currently active.

**Parameters:**
* `value_type` (*Any*, optional): Type hint, class, or object to resolve a randomizer
  for. Defaults to `None`.

**Returns:**
* `Any`: The resolved generator callable, or `None` if unresolved or `value_type` is
  `None`.

**Example usage:**
```python
test_registry = RandomizersRegistry()
test_registry.add(int, lambda: 42)

randomizer = test_registry.get_randomizer(int)
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

Instance-bound equivalent of the module-level `randomize()` function, executed within
this registry's own context.

**Parameters:**
* `value_type` (*Any*, optional): Target type hint. Defaults to `None`.
* `**kwargs` (*Any*): Extra keyword parameters forwarded to the resolved randomizer.

**Returns:**
* `Any`: The generated random value, or `None` if `value_type` is `None`.

**Raises:**
* `RandomizerNotFoundError`: If no matching randomizer could be resolved.
* `RandomizerExecutionFailedError`: If randomizer execution fails unexpectedly.

**Example usage:**
```python
test_registry = RandomizersRegistry()
value = test_registry.randomize(int)
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

Instance-bound equivalent of the module-level `bulk_randomizer()` function, executed
within this registry's own context.

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
test_registry = RandomizersRegistry()
results = test_registry.bulk_randomizer(int, str, bool)
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