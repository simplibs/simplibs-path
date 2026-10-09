# 📚 `simplibs.randomize.registry` — Package Overview

This document ties together the whole `registry` package: the class hierarchy behind it,
the ready-to-use global singleton (`RANDOMIZERS`), and the context-tracking mechanism
(`state/`) that lets the rest of the library resolve "the currently active registry"
without anyone having to pass it around explicitly.

---

## 🧭 Table of Contents

1. [The Class Hierarchy](#1-the-class-hierarchy)
2. [The `RANDOMIZERS` Singleton](#2-the-randomizers-singleton)
3. [State Logic: `_CURRENT_REGISTRY` & `get_current_registry`](#3-state-logic-_current_registry--get_current_registry)

---

## 1. The Class Hierarchy

Both concrete registry classes share a single abstract foundation:

```
RegistryBase[K, V]                       (MutableMapping + abstract subclass contract + context manager)
├── RandomizersRegistry[K, V]            (single-tier: user → defaults)
└── LocalRegistry[K, V]                  (three-tier: local_user → global_user → defaults)
```

* **`RegistryBase`** — the shared foundation. Provides the locked `_default_randomizers`
  reference and the `__enter__`/`__exit__` context-manager logic every registry needs,
  and declares `has_subclasses` / `subclass_search` as an abstract contract.  
  ➡️ [Full method-by-method reference (README_REGISTRY_BASE)](README_REGISTRY_BASE.md)


* **`RandomizersRegistry`** — the concrete class used both as the global singleton
  (`RANDOMIZERS`, see below) and as a fully standalone registry you can instantiate
  yourself (e.g. for isolated tests). Resolves lookups across two tiers: user overrides
  → defaults.  
  ➡️ [Full method-by-method reference (README_RANDOMIZERS_REGISTRY)](README_RANDOMIZERS_REGISTRY.md)


* **`LocalRegistry`** — the concrete class for scoped, temporary overrides. Keeps local
  mutations completely isolated while still reading through to the global singleton's
  own overrides. Resolves lookups across three tiers: local user overrides → global user
  overrides → defaults.  
  ➡️ [Full method-by-method reference (README_LOCAL_REGISTRY)](README_LOCAL_REGISTRY.md)


Both concrete classes are assembled from small, single-purpose mixins (`MappingDunders`,
`MappingMethods`, `SubclassMethods`, `KeyCeckers` — each with a `globals` and a `locals`
variant — plus the shared `commons` mixins `PublickHelpers` and `ContextualApi`). This
keeps each concern in its own short, atomized file rather than one large class body.

---

## 2. The `RANDOMIZERS` Singleton

`RANDOMIZERS` is a single, module-level instance of `RandomizersRegistry`, created once
when the package is imported. It's the default fallback every randomizer resolves
against unless a `LocalRegistry` (or another `RandomizersRegistry` used as a context
manager) is currently active.

```python
from .classes.RandomizersRegistry import RandomizersRegistry

RANDOMIZERS = RandomizersRegistry()
```

Because `RANDOMIZERS` is just a `RandomizersRegistry` instance, everything from the
[RandomizersRegistry reference](README_RANDOMIZERS_REGISTRY.md) applies to it directly
— you can use it as a dictionary (`RANDOMIZERS[str] = ...`), or through its own methods
(`RANDOMIZERS.add(...)`).

On top of that, the module exports a set of bound-method aliases, so common actions can
be imported and called directly at the module level without referencing `RANDOMIZERS`
explicitly:

| Function                      | Purpose                                        | Equivalent direct call                    |
|-------------------------------|------------------------------------------------|-------------------------------------------|
| `add_randomizer(key, value)`  | Registers a single randomizer.                 | `RANDOMIZERS.add(key, value)`             |
| `add_randomizers(mapping)`    | Registers multiple randomizers from a mapping. | `RANDOMIZERS.add_many(mapping)`           |
| `remove_randomizer(key)`      | Removes a single randomizer.                   | `RANDOMIZERS.remove(key)`                 |
| `remove_randomizers(keys)`    | Removes multiple randomizers.                  | `RANDOMIZERS.remove_many(keys)`           |
| `reset_randomizers()`         | Clears all user overrides.                     | `RANDOMIZERS.reset()`                     |
| `subclass_search(value_type)` | Looks up a randomizer by inheritance.          | `RANDOMIZERS.subclass_search(value_type)` |



**Example usage:**
```python
from simplibs.randomize.registry import add_randomizer
from simplibs.randomize import RANDOMIZERS

# These three lines are functionally identical:
add_randomizer(str, lambda: "custom-value")
RANDOMIZERS.add(str, lambda: "custom-value")
RANDOMIZERS[str] = lambda: "custom-value"
```

[▲ Back to top](#-table-of-contents)

---

## 3. State Logic: `_CURRENT_REGISTRY` & `get_current_registry`

This is the mechanism that makes registry switching transparent: functions like
`randomize()`, `get_randomizer()`, or `randomize_any()` never need a registry passed
into them explicitly — they simply ask "what's the currently active registry?" and get
the right answer, whether that's the global singleton or a temporarily activated
`LocalRegistry`.

### `_CURRENT_REGISTRY`

A `contextvars.ContextVar` that holds a reference to whichever registry is currently
"active," or `None` if no registry has been explicitly activated.

```python
from contextvars import ContextVar
from typing import TYPE_CHECKING, Optional

_CURRENT_REGISTRY: ContextVar[Optional["RegistryBase"]] = ContextVar(
    "_current_registry", default=None
)
```

Why `ContextVar` specifically, rather than a plain module-level variable? A plain global
would be shared and mutated across every thread and every concurrently running `asyncio`
task — meaning one task's `with LocalRegistry():` block could leak into, or get
overwritten by, another task's registry state. `ContextVar` solves this by giving each
thread and each async task its own independent "view" of the variable. Setting it in one
context never affects another.

The actual set/reset cycle happens inside `RegistryBase.__enter__` / `__exit__` (see the
[RegistryBase reference](README_REGISTRY_BASE.md#__enter__)):

```python
def __enter__(self) -> "RegistryBase":
    token = _CURRENT_REGISTRY.set(self)   # activates `self`, remembers a restore-point token
    self._context_tokens.append(token)
    return self

def __exit__(self, *exc_info) -> None:
    token = self._context_tokens.pop()
    _CURRENT_REGISTRY.reset(token)        # restores exactly what was active before
```

`ContextVar.set()` returns a `Token`, which `reset()` later uses to restore the *exact*
prior value — this is what makes nested `with` blocks (a `LocalRegistry` inside another
`LocalRegistry`) unwind correctly, each one restoring precisely the state before it was
entered.

[▲ Back to top](#-table-of-contents)

---

### `get_current_registry`

The single read-access point for "what registry should I use right now?" It's a small
function, but every randomizer lookup in the library ultimately goes through it.

```python
def get_current_registry() -> "RegistryBase":
    local_registry = _CURRENT_REGISTRY.get()

    return (
        RANDOMIZERS
        if local_registry is None
        else local_registry
    )
```

The logic is simple: read `_CURRENT_REGISTRY`. If nothing has been activated (`None` —
the default), fall back to the global `RANDOMIZERS` singleton. If a registry *has* been
activated via `with`, return that instance instead.

Because this is a plain read — it never sets or mutates `_CURRENT_REGISTRY` — you don't
call it directly in everyday usage. Activation always happens either through Python's
own `with registry:` syntax, or through the
[`ContextualApi`](README_RANDOMIZERS_REGISTRY.md#get_randomizer) methods
(`registry.randomize(...)`, `registry.get_randomizer(...)`,
`registry.bulk_randomizer(...)`), which wrap the call in `with self:` for you.

**Example usage:**
```python
from simplibs.randomize.registry.classes import LocalRegistry
from simplibs.randomize.registry.state import get_current_registry

print(get_current_registry())  # -> RANDOMIZERS (nothing active yet)

with LocalRegistry() as reg:
    reg.add(str, lambda: "override")
    print(get_current_registry())  # -> reg (the LocalRegistry instance)

print(get_current_registry())  # -> RANDOMIZERS again, automatically restored
```

### Where it's actually used

`get_current_registry()` is the very first thing `get_randomizer()` calls, before it
does anything else:

```python
def get_randomizer(value_type: Any = None) -> Any:
    if value_type is None:
        return None

    _RANDOMIZERS = get_current_registry()   # <-- resolves active registry here

    if value_type in _RANDOMIZERS:
        return _RANDOMIZERS[value_type]

    _origin = get_origin(value_type)
    if _origin is not None and _origin in _RANDOMIZERS:
        return _RANDOMIZERS[_origin]

    _value_type = type(value_type)
    if _value_type in _RANDOMIZERS:
        return _RANDOMIZERS[_value_type]

    if _RANDOMIZERS.has_subclasses():
        return _RANDOMIZERS.subclass_search(value_type)

    return None
```

Every step of `get_randomizer()`'s multi-step resolution pipeline — exact key match,
generic origin match, value-type match, and subclass search — runs against whatever
`get_current_registry()` returned, not necessarily the global singleton. This is exactly
what makes `LocalRegistry` overrides work transparently: nested type resolution (like
the item type inside `list[MyType]`, or a candidate type passed to
`randomize_any(MyType, int)`) all calls back into `get_randomizer()` internally, so it
automatically inherits whichever registry is currently active — no registry object ever
needs to be threaded manually through the call chain.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../_README.md)