from ..logic.checks._helpers import to_path
from ..logic.transformers._helpers import is_valid_suffix
from ..rules._helpers import (
    build_not_a_path_exception,
    build_path_rule_exception,
    check_path,
)

__all__ = [
    # turning a value into a path
    "to_path",
    # judging the shape of a suffix
    "is_valid_suffix",
    # building your own path rules
    "check_path",
    "build_path_rule_exception",
    "build_not_a_path_exception",
]


_DESIGN_NOTES = """
# Path Tools Sub-Package

## Purpose
The building blocks the library itself uses to write path rules and
path-aware functions, offered as a public toolkit — for `simplibs-file`
and for anyone who writes a rule of their own:

    from simplibs.path.tools import to_path, build_path_rule_exception

* `to_path(value)` — a `str`/`Path` becomes a `Path`; anything unusable
  (a blank string, a null byte, another type) becomes `None`, never an exception.
* `check_path(value, check)` — run a filesystem check on a value and answer
  `False` instead of raising; the wrapper every filesystem rule needs.
* `build_path_rule_exception(...)`, `build_not_a_path_exception(...)` — the
  failure card of a path rule, covering both "not a path at all" and "a path
  that fails the rule".
* `is_valid_suffix(suffix)` — the one definition of "what a suffix looks like"
  that `change_suffix` and `HasSuffix` share; `""` (no suffix) is valid.

## A Facade, Not a Move
Nothing lives here: the four functions stay where they are written
(`logic/checks/_helpers`, `logic/transformers/_helpers`, `rules/_helpers`) and
are only re-exported. Their internal location can change without breaking
anyone; what this package exports is the contract.

## One Rule: Nothing Inside `path` Imports From Here
Internal modules keep importing from the original locations. `tools` imports
`rules`, so an import in the other direction would be a cycle.

## Why Not the Root or `rules`
* The root exports the functions a USER calls on paths; these are for AUTHORS
  of rules, and a suffix-shape check is a predicate on text, not on a path.
* `rules.__all__` lists rules; mixing in functions would break
  `from simplibs.path.rules import *` and every "all of these are rules" assumption.

## Deliberately Not Here (Yet)
`PathPartIs` (a base class with protected hooks — exporting it is a promise
about its interface), `as_path_predicate`, `find_filename_problem`, `ScanEntry`:
nothing outside the library needs them today.

## Same Name as in `simplibs-exception`
`simplibs.exception.tools` holds that library's developer helpers; the same
word means the same kind of thing here.

## Domain Folder: `__all__`
As `rules` and `actions`, this package defines `__all__` and is not
re-exported from the package root.
"""