# 📚 `ALL_DEFAULT` — Built-in Default Randomizers

This document gives a complete overview of the internal dictionary structure that makes
up the library's built-in default randomizers — the fallback layer every registry
(`RandomizersRegistry`, `LocalRegistry`) reads from once no user override matches.

---

## 🧭 Table of Contents

* [1. The Root Registry (`ALL_DEFAULT`)](#1-the-root-registry-all_default)
* [2. Meta Types (`ALL_META_TYPES`)](#2-meta-types-all_meta_types)
* [3. Standalone Randomizers
  (`ALL_STAND_ALONE`)](#3-standalone-randomizers-all_stand_alone)
  * [Primitives (`ALL_RPRIMITIVES`)](#primitives-all_rprimitives)
  * [Special (`ALL_SPECIAL`)](#special-all_special)
  * [Temporal (`ALL_TEMPORAL`)](#temporal-all_temporal)
* [4. Type-Aware Randomizers
  (`ALL_TYPE_AWARE`)](#4-type-aware-randomizers-all_type_aware)
  * [Collections (`ALL_COLLECTIONS`)](#collections-all_collections)
  * [Structural (`ALL_STRUCTURAL`)](#structural-all_structural)

---

## A note on `MappingProxyType`

Every dictionary shown below is wrapped in `MappingProxyType`. This makes each one an
**immutable, read-only view** — the built-in defaults can never be accidentally mutated,
overwritten, or corrupted at runtime, no matter what code touches them. This is exactly
what `RegistryBase._default_randomizers` relies on: a single, permanently safe reference
shared by every registry instance 
(see the [RegistryBase reference](../state/README_REGISTRY_BASE.md#_default_randomizers)).

---

## 1. The Root Registry (`ALL_DEFAULT`)

`ALL_DEFAULT` is the single dictionary every registry ultimately falls back to. It's
simply the union of the two top-level groups below.

```python
ALL_DEFAULT = MappingProxyType({
    **ALL_META_TYPES,
    **ALL_STAND_ALONE,
    **ALL_TYPE_AWARE,
})
```

[▲ Back to top](#-table-of-contents)

---

## 2. Meta Types (`ALL_META_TYPES`)

Generators for special Python system meta-types and the value `None`.

```python
from typing import Any
from types import NoneType

ALL_META_TYPES = MappingProxyType({
    Any: randomize_any,
    NoneType: get_none,
})
```

[▲ Back to top](#-table-of-contents)

---

## 3. Standalone Randomizers (`ALL_STAND_ALONE`)

Groups all the primitive and special generators that don't require analyzing type
arguments.

```python
ALL_STAND_ALONE = MappingProxyType({
    **ALL_RPRIMITIVES,
    **ALL_TEMPORAL,
    **ALL_SPECIAL,
})
```

### Primitives (`ALL_RPRIMITIVES`)

Python's built-in primitive types, plus `Decimal`.

```python
from decimal import Decimal

ALL_RPRIMITIVES = MappingProxyType({
    bool: randomize_bool,
    int: randomize_int,
    float: randomize_float,
    str: randomize_str,
    bytes: randomize_bytes,
    Decimal: randomize_decimal,
})
```

### Special (`ALL_SPECIAL`)

Special system and object types.

```python
from pathlib import Path
from uuid import UUID

ALL_SPECIAL = MappingProxyType({
    Path: randomize_path,
    UUID: randomize_uuid,
})
```

### Temporal (`ALL_TEMPORAL`)

Date, time, and duration types.

```python
from datetime import date, datetime, time, timedelta

ALL_TEMPORAL = MappingProxyType({
    date: randomize_date,
    datetime: randomize_datetime,
    time: randomize_time,
    timedelta: randomize_timedelta,
})
```

[▲ Back to top](#-table-of-contents)

---

## 4. Type-Aware Randomizers (`ALL_TYPE_AWARE`)

Registries for generic types and structures that require inspecting their inner type
hints (e.g. nested types inside collections, or the variants inside a union).

```python
ALL_TYPE_AWARE = MappingProxyType({
    **ALL_COLLECTIONS,
    **ALL_STRUCTURAL,
})
```

### Collections (`ALL_COLLECTIONS`)

Python's standard collections that support generic typing.

```python
ALL_COLLECTIONS = MappingProxyType({
    dict: randomize_dict,
    list: randomize_list,
    set: randomize_set,
    tuple: randomize_tuple,
})
```

### Structural (`ALL_STRUCTURAL`)

Registries for advanced type-checking constructs.

```python
from typing import Literal, Union
from types import UnionType
from enum import Enum, EnumType, EnumMeta

ALL_STRUCTURAL = MappingProxyType({
    Literal: randomize_literal,
    UnionType: randomize_union,
    Union: randomize_union,
    Enum: randomize_enum,
    EnumType: randomize_enum,
    EnumMeta: randomize_enum,
})
```

> **A note on the aliases:** `ALL_STRUCTURAL` deliberately registers several different
  variants and internal representations for the same concept (e.g. `Union` vs. the
  modern `UnionType`, or `Enum`, `EnumType`, and `EnumMeta`). These aliases exist so the
  intended target is reliably caught regardless of which Python version you're on or how
  exactly the type hint was written.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../../_README.md)