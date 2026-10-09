# 🧱 `RegistryBase` — Shared Registry Foundation

`RegistryBase` is the common abstract foundation shared by both `RandomizersRegistry`
(the global singleton) and `LocalRegistry` (isolated local scopes). It does not
implement a working registry on its own — instead it provides three things every
registry needs:

1. A locked, read-only reference to the built-in default randomizers
   (`_default_randomizers`).


2. An abstract contract for subclass-based (inheritance-aware) lookups
   (`has_subclasses`, `subclass_search`) that every concrete registry must implement.


3. The context-manager machinery (`__enter__` / `__exit__`) that powers `with registry:`
   blocks and lets `get_current_registry()` resolve the currently active registry.

```python
from ...randomizers import ALL_DEFAULT

class RegistryBase(MutableMapping[K, V]):
    ...
```

## A note on `MutableMapping`

`RegistryBase` inherits from `collections.abc.MutableMapping[K, V]`. This is what allows
every registry to behave like a plain Python `dict` from the outside — supporting
`reg[key]`, `del reg[key]`, `key in reg`, `for key in reg`, `len(reg)`, and, for free, a
whole family of derived methods (`get`, `keys`, `values`, `items`, `update`,
`setdefault`, `popitem`) that `MutableMapping` builds automatically on top of a small
set of required primitives.

That small set — `__setitem__`, `__delitem__`, `__getitem__`, `__iter__`, `__len__` — is
**not** implemented in `RegistryBase` itself. `RegistryBase` stays intentionally
incomplete (it cannot be instantiated on its own) and leaves those five dunders to be
supplied by the `MappingDunders` mixins (`globals` or `locals` variant, depending on
which concrete class is being built). This keeps `RegistryBase` focused purely on what
is truly shared, while the actual storage/lookup behavior lives in the mixins described
in the other two READMEs.

---

## 🧭 Table of Contents

* [`__init__`](#__init__)
* [`_default_randomizers`](#_default_randomizers)
* [`has_subclasses`](#has_subclasses)
* [`subclass_search`](#subclass_search)
* [`__enter__`](#__enter__)
* [`__exit__`](#__exit__)

---

### `__init__`

Initializes the shared state every registry needs: a reference to the built-in default
randomizers, and an empty stack used to track context-manager activations.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `None`

**Example usage:**
```python
# Called implicitly via super().__init__() in RandomizersRegistry / LocalRegistry
class RandomizersRegistry(..., RegistryBase[K, V]):
    def __init__(self) -> None:
        super().__init__()
        self.__user_randomizers: dict[K, V] = {}
        self.__subclass_index: dict[K, V] = {}
```

**Under the hood:**
```python
def __init__(self) -> None:
    self.__default_randomizers = ALL_DEFAULT
    self._context_tokens: list = []
```

[▲ Back to top](#-table-of-contents)

---

### `_default_randomizers`

A read-only property exposing the shared dictionary of built-in default randomizers
(`ALL_DEFAULT`). Implemented as a property specifically to prevent it from being
accidentally reassigned — this is especially important for `LocalRegistry`, which shares
a reference to this same object rather than copying it.

**Parameters:**
* *(none — property getter)*

**Returns:**
* `dict`: The internal `ALL_DEFAULT` mapping of built-in type → randomizer callable.

**Example usage:**
```python
from simplibs.randomize.registry import RANDOMIZERS

# Inspecting the built-in fallback layer
print(len(RANDOMIZERS._default_randomizers))
```

**Under the hood:**
```python
@property
def _default_randomizers(self) -> dict:
    return self.__default_randomizers
```

[▲ Back to top](#-table-of-contents)

---

### `has_subclasses`

Abstract method. Every concrete registry must report whether it currently holds any
subclass-based (inheritance-aware) mappings. Used by `get_randomizer()` to decide
whether it's worth attempting an `issubclass()`-based search at all.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `bool`: `True` if at least one subclass mapping is registered, `False` otherwise.

**Example usage:**
```python
if RANDOMIZERS.has_subclasses():
    print("At least one custom base-class randomizer is registered.")
```

**Under the hood:**
```python
@abstractmethod
def has_subclasses(self) -> bool:
    """Checks whether any subclass mappings are registered."""
    ...
```

*(The actual implementation lives in `SubclassMethods` — see the `RandomizersRegistry`
and `LocalRegistry` READMEs.)*

[▲ Back to top](#-table-of-contents)

---

### `subclass_search`

Abstract method. Every concrete registry must implement the actual `issubclass()`-based
lookup, returning the first matching randomizer registered for a base class of
`value_type`.

**Parameters:**
* `value_type` (*Any*): The target class or type to check against registered base
  classes.

**Returns:**
* `V | None`: The matching randomizer callable, or `None` if no base class matches.

**Example usage:**
```python
class MyIntSubclass(int):
    pass

randomizer = RANDOMIZERS.subclass_search(MyIntSubclass)
```

**Under the hood:**
```python
@abstractmethod
def subclass_search(self, value_type: Any) -> V | None:
    """Looks up a randomizer registered for a base class of `value_type`."""
    ...
```

*(The actual implementation lives in `SubclassMethods` — see the `RandomizersRegistry`
and `LocalRegistry` READMEs.)*

[▲ Back to top](#-table-of-contents)

---

### `__enter__`

Activates the current registry instance in the active execution context by pushing it
onto the `_CURRENT_REGISTRY` context variable. This is what makes `with registry:` work,
and it's inherited unchanged by both `RandomizersRegistry` and `LocalRegistry` — neither
one overrides it.

**Parameters:**
* *(none — takes only `self`)*

**Returns:**
* `RegistryBase`: `self`, so the instance can be bound via `as`.

**Example usage:**
```python
with RANDOMIZERS as reg:
    # RANDOMIZERS is now the active context registry (a no-op in practice,
    # since it's already the fallback — see the Overview README for details)
    value = reg.randomize(int)
```

**Under the hood:**
```python
def __enter__(self) -> "RegistryBase":
    from ..state import _CURRENT_REGISTRY
    token = _CURRENT_REGISTRY.set(self)
    self._context_tokens.append(token)
    return self
```

[▲ Back to top](#-table-of-contents)

---

### `__exit__`

Restores the previously active registry once the `with` block ends, by popping the token
pushed during `__enter__` and resetting the `_CURRENT_REGISTRY` context variable to its
prior state. Supports nested `with` blocks correctly, since tokens are managed as a
stack.

**Parameters:**
* `*exc_info`: Standard context-manager exception info tuple (unused; exceptions are not
  suppressed).

**Returns:**
* `None`

**Example usage:**
```python
with LocalRegistry() as outer:
    outer.add(int, lambda: 1)
    with LocalRegistry() as inner:
        inner.add(int, lambda: 2)
        # inner is active here
    # outer is active again here
```

**Under the hood:**
```python
def __exit__(self, *exc_info) -> None:
    from ..state import _CURRENT_REGISTRY
    token = self._context_tokens.pop()
    _CURRENT_REGISTRY.reset(token)
```

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../_README.md)