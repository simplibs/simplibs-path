# 🎲 `simplibs-randomize`

[![PyPI](https://img.shields.io/pypi/v/simplibs-randomize)](https://pypi.org/project/simplibs-randomize/)
[![Python](https://img.shields.io/badge/python-3.11%2B-blue)](https://www.python.org/downloads/)
[![Licence](https://img.shields.io/badge/licence-MIT-green)](https://github.com/simplibs/simplibs-randomize/blob/main/LICENSE)

**Generate realistic test data effortlessly from Type Hints.**

A zero-friction Python library for generating randomized mock values directly from type
annotations, custom domain types, and generic structures. Fully configurable,
extensible, and isolated.

```python
from simplibs.randomize import randomize

randomize(int)                         # -> 42
randomize(list[str])                   # -> ["alpha", "bravo", "charlie"]
randomize(dict[str, Union[int, bool]]) # -> {"key_x": 105, "key_y": True}
```

---

## 🧭 The Core Philosophy

Writing realistic test fixtures or mock data generation code is often tedious and
error-prone. Developers repeatedly build ad-hoc custom generators or wrestle with overly
rigid mocking frameworks.

`simplibs-randomize` bridges this gap by acting as a **Type-Aware Randomization
Engine**. Pass any standard Python type, generic type hint (`Union`, `Literal`,
`Optional`), or custom class, and receive a valid instance instantly. It ships with a
single, ready-to-use global registry for everyday defaults while giving you
fine-grained, context-safe local overrides whenever your tests demand precision.

---

## 📦 Installation

```bash
pip install simplibs-randomize
```

---

## 🚀 Quick Start in 60 Seconds

### Level 1: Standalone Generators

Every randomizer can be called directly and independently — no setup required, and every
parameter is optional.

```python
from simplibs.randomize import randomize_int, randomize_str

age = randomize_int(min_value=18, max_value=99)
username = randomize_str(min_length=5, max_length=12)
```

### Level 2: Type-Driven Generation

Don't want to remember which function belongs to which type? Pass any type hint to
`randomize()` and let the library figure out the rest — including nested, generic
structures.

```python
from simplibs.randomize import randomize

user_id = randomize(int)
tags = randomize(list[str])
payload = randomize(dict[str, list[Union[int, bool]]])
```

### Level 3: Bulk Generation

Need several values at once? `bulk_randomizer` handles both positional and
dictionary-shaped requests.

```python
from simplibs.randomize import bulk_randomizer

payload = bulk_randomizer({
    "user_id": int,
    "username": (str, {"min_length": 5}),
    "is_active": bool,
})
# -> {"user_id": 482, "username": "aX9qL", "is_active": True}
```

---

## 🛠️ The Architecture: 3 Pillars

```
┌────────────────────────────────┐
│          Randomizers           │ ◄── Standalone & type-aware generator functions
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│            Registry            │ ◄── RANDOMIZERS singleton, RegistryBase, LocalRegistry
└──────────────┬─────────────────┘
               │
               ▼
┌────────────────────────────────┐
│         Core Functions         │ ◄── get_randomizer, randomize, bulk_randomizer
└────────────────────────────────┘
```

### 1. Randomizers (The Generators)

Every value-generating function in the library, grouped into Standalone (primitives,
special, temporal), Type-Aware (collections, structural), and Meta types — each
documented individually with parameters, defaults, examples, and full source.

➡️ [README_DEFAULT_RANDOMIZERS](https://github.com/simplibs/simplibs-randomize/blob/main/docs/randomizers/README_DEFAULT_RANDOMIZERS.md)

Every one of them is also indexed in the quick-reference table below.

### 2. Registry (The Storage & Scoping Layer)

The system that maps types to randomizer callables, resolves user overrides before
falling back to defaults, and supports fully isolated local scopes via context managers.

* **`RegistryBase`** — the shared abstract foundation (`MutableMapping` +
  context-manager logic).  
  ➡️ [README_REGISTRY_BASE](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_REGISTRY_BASE.md)   


* **`RandomizersRegistry`** — the concrete class behind the global `RANDOMIZERS`
  singleton, also usable as a fully standalone registry.  
  ➡️ [README_RANDOMIZERS_REGISTRY](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_RANDOMIZERS_REGISTRY.md)


* **`LocalRegistry`** — isolated, scoped overrides with transparent global fallback.  
  ➡️ [README_LOCAL_REGISTRY](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_LOCAL_REGISTRY.md)


* **The `RANDOMIZERS` singleton & context state** (`_CURRENT_REGISTRY`,
  `get_current_registry`) — how the active registry is resolved automatically,
  everywhere in the library.  
  ➡️ [README_STATE](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_STATE.md)


* **`ALL_DEFAULT`** — the full built-in dictionary structure every registry falls back
  to.  
  ➡️ [randomizers/README_ALL_DEFAULT](https://github.com/simplibs/simplibs-randomize/blob/main/docs/randomizers/README_ALL_DEFAULT.md)

### 3. Core Functions (The Entry Points)

The three top-level functions tying everything together: `get_randomizer` (resolution),
`randomize` (resolution + execution), and `bulk_randomizer` (batch processing).

➡️ [README_MAIN_FUNCTIONS](https://github.com/simplibs/simplibs-randomize/blob/main/docs/README_MAIN_FUNCTIONS.md)

---

## 📖 Randomizer Quick Reference

Every built-in randomizer, its parameters, and their defaults. For the full description,
examples, and implementation of each one, see
[README_DEFAULT_RANDOMIZERS](https://github.com/simplibs/simplibs-randomize/blob/main/docs/randomizers/README_DEFAULT_RANDOMIZERS.md).

### 1. Standalone Randomizers

#### 1.1 Primitives

| - - - - - Randomizer - - - - - | - - - - - - - - - -  Parameters (default) - - - - - - - - - -                                           |
|--------------------------------| ------------------------------------------------------------------------------------------------------- |
| `randomize_bool`               | `true_probability: float = 0.5`                                                                         |
| `randomize_bytes`              | `min_length: int = 5`<br>`max_length: int = 15`                                                         |
| `randomize_decimal`            | `min_value: float = 0.0`<br>`max_value: float = 1000.0`<br>`exponent: int = -2`                         |
| `randomize_float`              | `min_value: float = 0.0`<br>`max_value: float = 1000.0`<br>`ndigits: int = 2`                           |
| `randomize_int`                | `min_value: int = 0`<br>`max_value: int = 1000`                                                         |
| `randomize_str`                | `min_length: int = 5`<br>`max_length: int = 15`<br>`alphabet: str = ascii_letters + digits`             |

#### 1.2 Special

| - - - - - Randomizer - - - - - | - - - - - - - - - -  Parameters (default) - - - - - - - - - -                                           |
| ------------------------------ |---------------------------------------------------------------------------------------------------------|
| `randomize_path`               | `directory: str = "/tmp"`<br>`extension: str = ".txt"`<br>`name_length: int = 10`                       |
| `randomize_uuid`               | — (no parameters)                                                                                       |

#### 1.3 Temporal

| - - - - - Randomizer - - - - - | - - - - - - - - - -  Parameters (default) - - - - - - - - - -                                           |
| ------------------------------ |---------------------------------------------------------------------------------------------------------|
| `randomize_date`               | `start: date = date(2020, 1, 1)`<br>`end: date = date(2025, 12, 31)`                                    |
| `randomize_datetime`           | `start: datetime = datetime(2020, 1, 1)`<br>`end: datetime = datetime(2025, 12, 31)`                    |
| `randomize_time`               | `min_hour: int = 0`<br>`max_hour: int = 23`                                                             |
| `randomize_timedelta`          | `min_seconds: int = 0`<br>`max_seconds: int = 2592000` (30 days)                                        |

### 2. Type-Aware Randomizers

#### 2.1 Collections

| - - - - - Randomizer - - - - - | - - - - - - - - - -  Parameters (default) - - - - - - - - - -                                            |
| ------------------------------ |----------------------------------------------------------------------------------------------------------|
| `randomize_dict`               | `dict_type: Any = dict`<br>`min_length: int = 1`<br>`max_length: int = 5`                                |
| `randomize_list`               | `list_type: Any = list`<br>`min_length: int = 1`<br>`max_length: int = 5`                                |
| `randomize_set`                | `set_type: Any = set[str]`<br>`min_length: int = 1`<br>`max_length: int = 5`<br>`max_attempts: int = 50` |
| `randomize_tuple`              | `tuple_type: Any = tuple`<br>`min_length: int = 1`<br>`max_length: int = 5`                              |

#### 2.2 Structural

| - - - - - Randomizer - - - - - | - - - - - - - - - -  Parameters (default) - - - - - - - - - -                                            |
| ------------------------------ |----------------------------------------------------------------------------------------------------------|
| `randomize_enum`               | `enum_type: type[Enum] = Enum`<br>`exclude: Iterable[Enum] \| None = None`                               |
| `randomize_literal`            | `literal_type: Any = Literal`                                                                            |
| `randomize_union`              | `union_type: Any = UnionType`<br>`none_probability: float = 0.3`                                         |

### 3. Meta Types

| - - - - - Randomizer - - - - - | - - - - - - - - - -  Parameters (default) - - - - - - - - - -                                            |
| ------------------------------ |----------------------------------------------------------------------------------------------------------|
| `randomize_any`                | `*choices: Any`<br>`validate: bool = True`                                                               |
| `get_none`                     | — (no parameters)                                                                                        |

---

## 🗂️ The `RANDOMIZERS` Singleton & Registry Classes

Every randomizer lookup goes through a registry. By default, that's the global
`RANDOMIZERS` singleton — a ready-to-use instance you can treat as a dictionary, or
manage through explicit helper functions:

```python
from simplibs.randomize.registry import RANDOMIZERS, add_randomizer

# Dictionary-style
RANDOMIZERS[str] = lambda: "custom-value"

# Or via the exported helper functions
add_randomizer(str, lambda: "custom-value")
```

When you need isolation — in tests, or for a specific code path — `LocalRegistry` lets
you override behavior temporarily without touching the global state, while still
transparently seeing any global overrides:

```python
from simplibs.randomize.registry.classes import LocalRegistry

with LocalRegistry() as reg:
    reg.add(str, lambda: "TEST_OVERRIDE")
    value = reg.randomize(str)  # -> "TEST_OVERRIDE"

# Global RANDOMIZERS is untouched outside the `with` block
```

This all works without ever having to pass a registry object around explicitly — every
core function automatically resolves "whichever registry is currently active" behind the
scenes.

➡️ Full class-by-class, method-by-method breakdown, plus the singleton and
context-state mechanics:

* [README_REGISTRY_BASE](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_REGISTRY_BASE.md)
* [README_RANDOMIZERS_REGISTRY](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_RANDOMIZERS_REGISTRY.md)
* [README_LOCAL_REGISTRY](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_LOCAL_REGISTRY.md)
* [README_STATE](https://github.com/simplibs/simplibs-randomize/blob/main/docs/state/README_STATE.md)

---

## 🏷️ Building Custom Randomizers: `value_type_name`

When writing your own randomizers — especially ones that need to know *which* type hint
they were actually resolved for (containers, unions, or any generic-aware generator) —
you don't need to pass that information manually through `kwargs`. The
`@value_type_name` decorator marks a parameter to receive it automatically.

```python
from simplibs.randomize.tools.decorator import value_type_name

@value_type_name("my_type")
def randomize_my_container(my_type: Any = None, *, min_length: int = 1) -> Any:
    ...
```

Once decorated, calling `randomize(my_type_hint)` automatically injects `my_type_hint`
into the `my_type` parameter — unless you've already supplied it explicitly, in which
case your value always wins.

**Under the hood:**
```python
def value_type_name(param_name: str) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """Decorator marking a function parameter to receive the target value type automatically."""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:

        # 1. Input validation
        if not isinstance(param_name, str):
            raise_param_name_is_not_str(param_name, func)

        # 2. Attach parameter metadata attribute
        func._value_type_name = param_name

        # 3. Return the modified callable
        return func

    return decorator
```

This is exactly the mechanism `randomize()` itself relies on internally for every
built-in type-aware randomizer (`randomize_dict`, `randomize_list`, `randomize_union`,
...) — see [README_MAIN_FUNCTIONS](https://github.com/simplibs/simplibs-randomize/blob/main/docs/README_MAIN_FUNCTIONS.md#2-randomize)
for the injection logic on the calling side.

---

## ⚠️ Exceptions

Every exception raised by `simplibs-randomize` is built on top of
[`simplibs.exception.SimpleException`](https://pypi.org/project/simplibs-exception/) —
meaning failures don't just crash, they explain what went wrong, what was expected, and
how to fix it, instead of a bare traceback.

The library's single base exception is `RandomizeError`:

```python
from simplibs.exception import SimpleException

class RandomizeError(SimpleException):
    """Base exception class for all errors originating from the SimpleRandom library."""

    # Skip internal library frames when generating error location metadata.
    # This ensures that error messages point to user code rather than internal
    # implementation details, unless no user-level frames remain.
    _skip_locations = ("simplibs/random",)
```

Every error raised internally passes through `RandomizeError`, so it's always catchable
that way. On top of that, individual call sites can additionally pass a native exception
type (e.g. `TypeError`, `KeyError`) via `exception=...`. `SimpleException` then
dynamically injects that type into the raised exception's inheritance chain — so the
same error becomes catchable both as `RandomizeError` *and* as the native type you'd
naturally expect:

```python
raise RandomizeError(
    error_name="UNSUPPORTED CHOICE TYPES",
    label="choices",
    value=unknown_types,
    problem="The provided choices contain unsupported types for Any.",
    expected="Registered types in global scope.",
    how_to_fix="Register the type first, e.g. RANDOMIZERS.add(MyType, my_randomizer).",
    exception=TypeError,
)

# Catchable both ways:
try:
    ...
except RandomizeError:
    ...
except TypeError:
    ...
```

If a call site doesn't pass `exception=...` at all, the error is still fully catchable
via `RandomizeError` alone.

---

## 🧩 A Note on Scope

`simplibs-randomize` deliberately ships with a solid, well-tested **core** rather than
an exhaustive catalogue of every possible type under the sun. It covers the primitives,
collections, and structural constructs you'll actually reach for day to day — and the
registry/override system exists precisely so you can extend it with your own
domain-specific randomizers as your needs grow, without ever having to modify the
library itself. Think of it as a skeleton built to be used immediately *and* built upon.

---

## ☯️ About simplibs

All libraries in the **simplibs** (Simple Libraries) ecosystem share a common
engineering philosophy:

* **Dyslexia-friendly:**
We actively minimize cognitive load. Code is atomized into small, self-contained units,
files are named directly after the logical task they perform, and explanations describe
*why* something is designed, not just *what* it is.
* **Programmer's Zen:**
Nothing should be missing, and nothing should be superfluous. We value clean execution
paths and robust, understandable code architectures over rushed, messy feature sets.
* **Defensive Style:**
We actively anticipate edge cases and failure modes so that only safe operational paths
remain. Our code is built to degrade gracefully rather than crash unexpectedly.
* **Minimalism:**
Find the most direct path to the goal in as few operational steps as possible without
taking shortcuts on safety, readability, or completeness.
* **Code as Craft:**
Code should be pleasant to look at, readable at a glance, and evoke structural harmony.
We treat software engineering as a precision trade.

---

### 🤝 Contributing & Community

This is an **open-source project** built with love and care. We strongly believe in
community collaboration and welcome any feedback, bug reports, or feature ideas!

* **Want to contribute?** Feel free to open an Issue or submit a Pull Request.
* **Want to get in touch?** If you'd like to discuss the project further, collaborate,
  or just say hello, feel free to open a GitHub Issue or start a Discussion.

---

### 📝 License

This library is released under the **MIT License**. Build great things!

---

[▲ Back to Top](#-simplibs-randomize)