from .MAX_NAME_LENGTH import MAX_NAME_LENGTH
from .WINDOWS_FORBIDDEN_CHARS import WINDOWS_FORBIDDEN_CHARS
from .WINDOWS_RESERVED_NAMES import WINDOWS_RESERVED_NAMES


_DESIGN_NOTES = """
# Path Checks Constants Sub-Package

## Purpose
Platform-specific and universal name constraints (lengths and forbidden elements)
used during filename validation.

## Internal Components Registry

| Component                 | Type     | Description                                                          |
| :------------------------ | :------- | :------------------------------------------------------------------- |
| `MAX_NAME_LENGTH`         | Constant | The 255 limit on a single name.                                      |
| `WINDOWS_FORBIDDEN_CHARS` | Constant | Characters Windows forbids in names.                                 |
| `WINDOWS_RESERVED_NAMES`  | Constant | Reserved Windows device names (`CON`, `NUL`, `COM1`, ...).           |
"""