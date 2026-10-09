# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.1] - 2026-09-07

### 🐛 Fixed

* **Root Exception `skip_locations` Field**:  
  Renamed `_skip_locations` to `skip_locations` in `RandomizeError` to align with the constructor contract of `simplibs-exception`. This ensures internal library stack frames are correctly filtered out from tracebacks, pointing diagnostics directly to user code.

### 📋 Improved

* **Core Dependency Update**:  
  Upgraded `simplibs-exception` to `1.0.2` to resolve type checker warnings (`PyTypeChecker`) when using context-managed test helpers.

---

## [0.1.0] - 2026-08-12

### ✨ Added

#### Core Functions

* `randomize(value_type, **kwargs)` — primary facade resolving and generating a random value for any type hint in one call
* `get_randomizer(value_type)` — resolution dispatcher returning the matching generator callable without executing it
* `bulk_randomizer(*items, get_randomizers=False)` — batch generation across multiple type specifications, supporting both positional and dictionary-shaped input

#### Standalone Randomizers

* Primitives: `randomize_bool`, `randomize_bytes`, `randomize_decimal`, `randomize_float`, `randomize_int`, `randomize_str`
* Special: `randomize_path`, `randomize_uuid`
* Temporal: `randomize_date`, `randomize_datetime`, `randomize_time`, `randomize_timedelta`

#### Type-Aware Randomizers

* Collections: `randomize_dict`, `randomize_list`, `randomize_set`, `randomize_tuple`
* Structural: `randomize_enum`, `randomize_literal`, `randomize_union`

#### Meta Types

* `randomize_any(*choices, validate=True)` — generic value generation across candidate types
* `get_none()` — explicit `None` generator for meta-type resolution

#### Registry & Scoping System

* `RegistryBase` — shared abstract foundation (`MutableMapping` + context-manager protocol)
* `RandomizersRegistry` — concrete registry class powering both the global singleton and fully standalone instances
* `LocalRegistry` — isolated, scoped registry with transparent three-tier fallback (`local_user` → `global_user` → `defaults`)
* `RANDOMIZERS` — ready-to-use global singleton, with exported helper functions (`add_randomizer`, `add_randomizers`, `remove_randomizer`, `remove_randomizers`, `reset_randomizers`, `subclass_search`)
* `_CURRENT_REGISTRY` / `get_current_registry()` — `ContextVar`-backed active-registry resolution, enabling thread-safe and async-safe local overrides without manual registry passing
* `ALL_DEFAULT` — immutable (`MappingProxyType`) built-in dictionary structure backing every registry's fallback layer

#### Extensibility

* `@value_type_name(param_name)` — decorator enabling custom randomizers to automatically receive the resolved target type hint as a keyword argument
* Full support for registering custom randomizers, both globally (`RANDOMIZERS.add(...)`) and locally (`LocalRegistry`), including automatic subclass (`issubclass`) indexing

#### Exceptions

* `RandomizeError` — single base exception for the library, built on `simplibs.exception.SimpleException`, producing structured, actionable diagnostic output instead of bare tracebacks
* Dual catchability: every raised error is catchable via `RandomizeError`, and additionally via a native exception type (e.g. `TypeError`, `KeyError`) when one is supplied at the raise site

#### Documentation

* Full method-by-method reference documentation for every randomizer, registry class, and core function
* Dedicated documentation for the registry architecture, the `RANDOMIZERS` singleton, and the context-state mechanism
* Complete built-in randomizer quick-reference table

#### Quality Assurance

* Test suite covering randomizers, registries, context-scoping, and core resolution functions
* Unit and integration tests validating fallback precedence, subclass resolution, and error handling

#### Dependencies

* `simplibs-exception` — structured exception framework underlying `RandomizeError`
* `simplibs-sentinels` — sentinel values (`UNSET`) for distinguishing unset arguments from `None`

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)