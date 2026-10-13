from typing import Annotated
from simplibs.rules import is_bool, is_int, ge

RecursionDepth = Annotated[bool | int, is_bool | (is_int & ge(0))]
"""How deep a recursive scan may go.

- `True`: infinite recursion.
- `False`: no recursion (only the starting entries).
- A non-negative `int` (`0`, `1`, `2`, ...): maximum depth of traversal.
"""


_DESIGN_NOTES = """
# RecursionDepth — controlling traversal depth

## Purpose
A single shared annotation for recursive functions (`collect_paths`, `walk_tree`)
to validate depth constraints uniformly across the library.

---

## 1. Why `bool` Combined With `int`

In Python APIs, passing `True` or `False` is a clean and readable way to enable
or disable recursion entirely without remembering numeric constants like `-1`
or `sys.maxsize`. Combining `bool` with non-negative integers (`ge(0)`) gives
the exact semantics needed: infinite, disabled, or an exact maximum depth limit.

## 2. Boundary Enforcement

Negative integers (e.g., `-1`) are strictly rejected by `ge(0)`, preventing invalid
configurations at the `@validate_call` boundary.
"""