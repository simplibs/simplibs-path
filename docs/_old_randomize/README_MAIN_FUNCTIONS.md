# ⚙️ Core Functions: `get_randomizer`, `randomize` & `bulk_randomizer`

This document covers the three top-level functions that make up the library's main
operational interface, plus the small internal helpers that power `bulk_randomizer`.

* **`get_randomizer(value_type)`** — the resolution engine.  
  Finds the matching randomizer callable for a type, without calling it.


* **`randomize(value_type, **kwargs)`** — the execution facade.  
Resolves *and* immediately generates a value.


* **`bulk_randomizer(*items, get_randomizers=False)`** — the batch layer.  
Runs either of the above across many type specifications at once.


All three are context-aware: they resolve against whichever registry is currently active
— the global `RANDOMIZERS` singleton by default, or a `LocalRegistry` if one is active via `with`.  
See [`README_REGISTRY_OVERVIEW.md`](README_REGISTRY_OVERVIEW.md#3-state-logic-_current_registry--get_current_registry)
for the full mechanism behind that.

---

## 🧭 Table of Contents

* [1. `get_randomizer`](#1-get_randomizer)
* [2. `randomize`](#2-randomize)
* [3. `bulk_randomizer`](#3-bulk_randomizer)
  * [`process_item`](#process_item)
  * [`extract_type_and_kwargs`](#extract_type_and_kwargs)

---

## 1. `get_randomizer`

The resolution dispatcher of the library. Given a type hint, class, or object, it
searches the active registry and returns the matching generator **callable** — without
invoking it. If nothing matches, or the input is `None`, it safely returns `None` rather
than raising.

**Parameters:**
* `value_type` (*Any*, optional): Type hint, class, or object to resolve a randomizer
  for. Defaults to `None`.

**Returns:**
* `Any`: The resolved generator callable, or `None` if unresolved or `value_type` is
  `None`.

**Example usage:**
```python
from simplibs.randomize import get_randomizer

# Get the generator without running it yet
int_generator = get_randomizer(int)
if int_generator:
    value = int_generator(min_value=10, max_value=20)

# Works for generic type hints too
list_generator = get_randomizer(list[str])
```

**Under the hood:**
```python
def get_randomizer(
    value_type: Any = None,
) -> Any:
    # 1. Filter out None value
    if value_type is None:
        return None

    # 2. Retrieve the active registry (supporting local overrides via context or fallback)
    _RANDOMIZERS = get_current_registry()

    # 3. Direct key lookup
    if value_type in _RANDOMIZERS:
        return _RANDOMIZERS[value_type]

    # 4. Origin type lookup (for generic type hints like list[int], dict[str, Any])
    _origin = get_origin(value_type)
    if _origin is not None and _origin in _RANDOMIZERS:
        return _RANDOMIZERS[_origin]

    # 5. Value type lookup (resolves types via type(value_type))
    _value_type = type(value_type)
    if _value_type in _RANDOMIZERS:
        return _RANDOMIZERS[_value_type]

    # 6. Inheritance search (subclass lookup)
    if _RANDOMIZERS.has_subclasses():
        return _RANDOMIZERS.subclass_search(value_type)

    # 7. Not found
    return None
```

### The resolution pipeline, step by step

1. **`None` guard.** Returns `None` immediately — this is what allows optional fields or
   unset type hints to pass through harmlessly instead of forcing every caller to check
   for `None` first.


2. **Active registry acquisition (`_RANDOMIZERS = get_current_registry()`).** This is
   the step that makes the whole registry system transparent. It doesn't hardcode a
   reference to the global `RANDOMIZERS` singleton — instead it asks "what registry is
   active right now?" If a `LocalRegistry` is currently active via a `with` block (or
   via its own `.get_randomizer(...)` / `.randomize(...)` methods), *that* instance is
   used for every step below instead. See
   [`get_current_registry`](README_REGISTRY_OVERVIEW.md#get_current_registry) for the
   full explanation.
   > The variable is deliberately named `_RANDOMIZERS` (capitalized) even though it may
     hold a `LocalRegistry` — it's a mental anchor: in the overwhelming majority of
     calls, it *is* the global singleton, and the capitalized spelling keeps that
     association visible at a glance.


3. **Exact key lookup (`value_type in _RANDOMIZERS`).** Handles direct matches: `int`,
   `str`, `Literal['a', 'b']`, `Union[...]`, or any custom type explicitly registered.


4. **Generic origin resolution (`get_origin(value_type)`).** Unwraps parameterized
   generics down to their origin — `list[int]` → `list`, `dict[str, Any]` → `dict` — so
   the container-level randomizer can take over and handle the inner type arguments
   itself.


5. **Value type inspection (`type(value_type)`).** Falls back to inspecting the type of
   the input itself.
   > **Design note on Enums:** custom `Enum` subclasses are deliberately intercepted
     here, because `type(SomeEnum)` evaluates to `EnumType`/`EnumMeta`. This means that
     unless a specific `Enum` subclass is explicitly registered as a user override, step
     6 (subclass search) never even gets a chance to run for it — step 5 already
     resolves it first.


6. **Subclass search (`_RANDOMIZERS.subclass_search(value_type)`).** A linear
   `issubclass()` scan across registered base types. Automatically skipped entirely if
   the active registry reports `has_subclasses() == False`, avoiding wasted work when no
   inheritance-based overrides exist.


7. **Not found → `None`.** No exception. This exception-free contract is what lets
   `randomize()` decide, on its own terms, how to react to an unresolved type.

[▲ Back to top](#-table-of-contents)

---

## 2. `randomize`

The library's main entry-point facade. In one call, it resolves the matching randomizer
(via `get_randomizer`), automatically injects the original type hint back into the call
if the randomizer needs it, executes it, and returns the generated value — wrapping any
runtime failure into a domain-specific exception.

**Parameters:**
* `value_type` (*Any*, optional): Target type hint, class, or type construct (`int`,
  `str`, `dict[str, int]`, `Union[int, str]`, ...). Defaults to `None`.
* `**kwargs` (*Any*): Extra keyword parameters forwarded directly to the resolved
  randomizer (e.g. `min_value`, `max_length`).

**Returns:**
* `Any`: The generated random value, or `None` if `value_type` is `None`.

**Raises:**
* `RandomizerNotFoundError`: If no matching randomizer could be resolved for
  `value_type`.
* `RandomizerExecutionFailedError`: If the resolved randomizer raises during execution.

**Example usage:**
```python
from simplibs.randomize import randomize

# Simple primitives
age = randomize(int, min_value=18, max_value=99)
name = randomize(str, min_length=5, max_length=10)

# Nested / composite structures
data = randomize(dict[str, list[int]])
```

**Under the hood:**
```python
def randomize(
    value_type: Any = None,
    **kwargs: Any,
) -> Any:
    # 1. Filter out None value input
    if value_type is None:
        return None

    # 2. Resolve randomizer callable or raise error
    randomizer = get_randomizer(value_type)
    if randomizer is None:
        raise_randomizer_not_found(value_type)

    # 3. Inject value_type into kwargs via _value_type_name metadata (if present)
    param_name = getattr(randomizer, "_value_type_name", None)
    if param_name is not None:
        kwargs.setdefault(param_name, value_type)

    # 4. Compute and return generated value wrapped in error safety
    try:
        return randomizer(**kwargs)

    # 5. Handle unexpected runtime execution failure
    except Exception as err:
        randomizer: Callable[..., Any]
        raise_randomizer_execution_failed(
            value_type=value_type,
            randomizer=randomizer,
            kwargs=kwargs,
            original_exception=err,
        )
```

### Execution flow, step by step

1. **`None` guard.** Same pass-through contract as `get_randomizer` — no exception for
   `None`.


2. **Resolution phase.** Delegates to `get_randomizer(value_type)`. Since
   `get_randomizer` already reads the active registry via `get_current_registry()`,
   `randomize()` automatically inherits the same local-override awareness without doing
   anything extra itself.


3. **Metadata parameter injection.** This is the mechanism that lets type-aware
   randomizers (like `randomize_dict`, `randomize_list`, `randomize_union`) know *which*
   parameterized type hint they were actually resolved for, even though `get_randomizer`
   only returned a plain callable.
   * Standalone randomizers (`randomize_bool`, `randomize_int`, ...) don't need this —
     they only take configuration kwargs like `min_value`.
   * Type-aware randomizers are marked with the `@value_type_name("param_name")`
     decorator, which stores the target parameter name as `_value_type_name` metadata on
     the function.
   * `kwargs.setdefault(param_name, value_type)` injects the original type hint under
     that parameter name — but only if the caller didn't already pass it explicitly.
     This means `randomize(dict[str, int])` works out of the box, while `randomize(dict,
     dict_type=dict[str, int])` still lets an explicit override win.


4. **Execution, wrapped for safety.** The resolved randomizer is called with the
   (possibly injected) `kwargs`, inside a `try`/`except`.


5. **Failure wrapping.** Any exception raised during execution is caught and re-raised
   as `RandomizerExecutionFailedError`, carrying the original `value_type`, the
   `randomizer` that failed, the `kwargs` it was called with, and the
   `original_exception` — giving full diagnostic context instead of a bare traceback
   from deep inside a generator.

[▲ Back to top](#-table-of-contents)

---

## 3. `bulk_randomizer`

Generates (or resolves) values for multiple type specifications in a single call.
Accepts either positional arguments (returns a `tuple`) or a single dictionary (returns
a `dict`, preserving the original keys).

**Parameters:**
* `*items` (*Any*): One or more target specifications. Each item is either a standalone
  type hint, or a 2-tuple of `(value_type, kwargs_mapping)`. If a single `dict` is
  passed instead, its values are interpreted the same way (type hint or 2-tuple) and the
  result is returned keyed by the original dict's keys.
* `get_randomizers` (*bool*, optional): If `True`, returns the resolved generator
  callables instead of executing value generation. Defaults to `False`.

**Returns:**
* `Any`: A `tuple` of generated values/randomizers for positional input, or a `dict`
  mirroring the input keys for dictionary input.

**Example usage:**
```python
from simplibs.randomize import bulk_randomizer

# Positional variant -> tuple
age, name, price = bulk_randomizer(
    int,
    (str, {"min_length": 10, "max_length": 20}),
    (float, {"min_value": 1.0, "max_value": 100.0}),
)

# Dictionary variant -> dict, same keys
payload = bulk_randomizer({
    "user_id": int,
    "username": (str, {"min_length": 5}),
    "is_active": bool,
})
# -> {"user_id": 482, "username": "aX9qL", "is_active": True}

# Retrieve callables instead of values
generators = bulk_randomizer(int, str, get_randomizers=True)
```

**Under the hood:**
```python
def bulk_randomizer(
    *items: Any,
    get_randomizers: bool = False,
) -> Any:
    # 1. Detect dictionary input variant (single argument that is a dict)
    if len(items) == 1 and isinstance(items[0], dict):
        return {
            name: process_item(item, get_randomizers=get_randomizers)
            for name, item in items[0].items()
        }

    # 2. Standard positional tuple variant
    return tuple(
        process_item(item, get_randomizers=get_randomizers)
        for item in items
    )
```

### How it dispatches

1. **Dictionary detection.** If exactly one argument was passed *and* it's a `dict`,
   `bulk_randomizer` switches into "mapping mode": every value in that dict is treated
   as its own item specification, and the result dict mirrors the same keys.
2. **Positional fallback.** Otherwise, every positional argument is treated as its own
   item specification, and the results come back as a `tuple` in the same order.
3. Both branches delegate the actual per-item work to [`process_item`](#process_item) —
   `bulk_randomizer` itself contains no resolution or generation logic at all, only the
   shape-detection and iteration.

[▲ Back to top](#-table-of-contents)

---

### `process_item`

*(Internal helper, `simplibs.randomize.tools._bulk_helpers.process_item`)*

The per-item dispatcher used internally by `bulk_randomizer` for every entry it
processes — whether that entry came from a positional argument or a dictionary value.

**Parameters:**
* `item` (*Any*): A single item specification — either a standalone type hint, or a
  `(value_type, kwargs)` 2-tuple.
* `get_randomizers` (*bool*, keyword-only): If `True`, resolves and returns the
  randomizer callable instead of generating a value. Defaults to `False`.

**Returns:**
* `Any`: The resolved randomizer callable (if `get_randomizers=True`), or the generated
  random value.

**Example usage:**
```python
# Not called directly in normal usage — this is what bulk_randomizer
# runs internally for each item you pass it.
from simplibs.randomize.tools._bulk_helpers import process_item

value = process_item((int, {"min_value": 1, "max_value": 10}))
```

**Under the hood:**
```python
def process_item(
    item: Any,
    *,
    get_randomizers: bool = False,
) -> Any:
    from ...get_randomizer import get_randomizer
    from ...randomize import randomize

    # 1. Normalize item into value_type and keyword arguments mapping
    value_type, kwargs = _extract_type_and_kwargs(item)

    # 2. Return either resolved randomizer callable or execute randomized generation
    return (
        get_randomizer(value_type)
        if get_randomizers
        else randomize(value_type, **kwargs)
    )
```

Two things worth noting:
* It first normalizes the raw `item` via
  [`extract_type_and_kwargs`](#extract_type_and_kwargs), so both branches below always
  work with a clean `(value_type, kwargs)` pair regardless of which input shape was
  originally passed.
* In `get_randomizers=True` mode, `kwargs` is deliberately discarded — since no call is
  made, there's nothing to pass keyword arguments *to*. Only `randomize()` mode actually
  consumes `kwargs`.

[▲ Back to top](#-table-of-contents)

---

### `extract_type_and_kwargs`

*(Internal helper, `simplibs.randomize.tools._bulk_helpers._extract_type_and_kwargs`)*

Normalizes any single bulk-input item into a consistent `(value_type, kwargs_mapping)`
pair, so the rest of the pipeline never has to branch on input shape again.

**Parameters:**
* `item` (*Any*): A standalone type hint, or a 2-element `(value_type, kwargs_mapping)`
  tuple.

**Returns:**
* `tuple[Any, Mapping[str, Any]]`: The normalized `(value_type, kwargs)` pair. `kwargs`
  is an empty `dict` if none was supplied.

**Raises:**
* `BulkRandomizerInvalidKwargsError`: If a kwargs mapping is provided but contains
  non-string keys.

**Example usage:**
```python
extract_type_and_kwargs(int)
# -> (int, {})

extract_type_and_kwargs((int, {"min_value": 1, "max_value": 10}))
# -> (int, {"min_value": 1, "max_value": 10})
```

**Under the hood:**
```python
def _extract_type_and_kwargs(
    item: Any,
) -> tuple[Any, Mapping[str, Any]]:
    # 1. Detect kwargs tuple format: 2-element tuple where 2nd element is a Mapping (dict, Kwargs wrapper, etc.)
    if (
        isinstance(item, tuple)
        and len(item) == 2
        and isinstance(item[1], Mapping)
    ):

        # 1.1 Validate that all keys in the mapping are string parameter names
        if not all(isinstance(key, str) for key in item[1]):
            raise_not_all_keys_are_str(item)

        # 1.2 Return extracted type hint and keyword argument mapping
        return item[0], item[1]

    # 2. Return original item as value_type with an empty kwargs dictionary
    return item, {}
```

**Supported input shapes:**

| Input                                      | Result                                     |
|--------------------------------------------|--------------------------------------------|
| `int`                                      | `(int, {})`                                |
| `list[str]`                                | `(list[str], {})`                          |
| `(int, {"min_value": 1, "max_value": 10})` | `(int, {"min_value": 1, "max_value": 10})` |

> **Why `collections.abc.Mapping` instead of a strict `dict`?** Checking against
  `Mapping` rather than `dict` allows any mapping-like object to serve as the kwargs
  container. A plain `dict` is fully sufficient for everyday use; the broader `Mapping` 
  check simply avoids ambiguity in more advanced cases where a raw dict could otherwise 
  be mistaken for the target type itself.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../_README.md)