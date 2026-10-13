_DESIGN_NOTES = """
# Path Core Logic Package

## Purpose
The functional core of `simplibs-path`: plain, reusable functions that work on
their own, with no knowledge of the `Rule` or `Action` layers. `rules/` and
`actions/` are thin layers built *on top of* these functions — a rule wraps a
check, an action wraps a function — never the other way round.

This package groups; it does not export. It has no imports of its own, so
importing it costs nothing and creates no import cycles. The main package
`__init__` (`simplibs.path`) reaches into the four sub-packages below and
propagates their public names.

## Internal Components Registry

| Sub-package    | Kind                     | What it holds                                                                                   |
| :------------- | :----------------------- | :---------------------------------------------------------------------------------------------- |
| `transformers` | Pure path arithmetic     | `normalize_path`, `rebase_path`, `relativize_path`, `change_suffix`, `make_unique_path` — path in, path out. |
| `checks`       | Predicates with real logic | `is_empty_dir`, `is_hidden_path`, `is_path_readable`, `is_path_writable`, `is_valid_filename`, `is_within` — a `bool`, never an exception for disk problems. |
| `ensure`       | Changes the disk         | `ensure_dir`, `ensure_file`, `ensure_parent_dir` — make a filesystem state true, return the normalized path. |
| `scanners`     | Looks at a directory tree | `collect_paths`, `collect_files`, `collect_dirs`, `iter_paths`, `filter_paths`, plus the `ignore_names` constants. |

## Layering
The packages depend on each other in one direction only:

* `transformers` and `checks` are leaves — neither imports the other.
* `ensure` and `scanners` build on `transformers` (every path is normalized first).

Two small helpers are deliberately shared with the `rules/` package, which
imports them directly: `to_path` (in `checks/_helpers`) and `is_valid_suffix`
(in `transformers/_helpers`). That keeps one definition of "a usable path"
and "a suffix shape" for functions and rules alike.

## Why `logic` Is Its Own Folder
Without it, the package root would mix four logic packages with `rules/`,
`actions/` and `annotations/` — seven siblings of very different kinds. Grouping
the logic leaves the root readable as a map: *logic* (`logic`),
*vocabulary of predicates* (`rules`), *vocabulary of pipeline steps*
(`actions`) and *shared types* (`annotations`).
"""
