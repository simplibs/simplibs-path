# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/),
and this project adheres to [Semantic Versioning](https://semver.org/).

---

## [0.1.0] - 2026-10-11

### ✨ Added

#### Transformers — path in, path out

* `normalize_path(path, *, resolve_symlinks=True)` — absolute,
  `~`-expanded path with relative parts collapsed; symlinks resolved
  by default or kept as written; the path does not have to exist
* `normalize_entry_path(path)` — resolves the containing directory
  while preserving the final name as written, even if it is a symlink
* `rebase_path(path, *, source_root, target_root, new_suffix=None)` —
  maps a path from one root directory to the same place under another,
  optionally with a new suffix
* `relativize_path(path, *, root)` — expresses a path relative to
  a root directory
* `change_suffix(path, new_suffix)` — lexical replacement, addition
  or removal of the last suffix, with the suffix shape validated up front
* `make_unique_path(path, *, max_attempts=1000)` — returns the path,
  or the first free numbered variant (`name (1).ext`, `.tar.gz`-aware);
  a broken symlink counts as taken

#### Checks — predicates that never raise

* `is_path_readable(path)` — a file that can be opened, or a directory
  that can be listed
* `is_path_writable(path)` — probes whether a path could be written
  to now, without creating or changing anything
* `is_empty_dir(path)` — an existing, listable directory with no entries
* `is_hidden_path(path, *, check_attributes=False)` — dot-prefixed
  final name, optionally the Windows hidden attribute
* `is_within(path, root, *, resolve_symlinks=True, allow_equal=True)` —
  symlink-safe containment check, the path-traversal guard
* `is_valid_filename(name, *, portable=True)` — usable file name,
  portable across Windows and POSIX by default, with the exact reason
  available for failure messages

#### Ensure — make a filesystem state true

* `ensure_dir(path)` — guarantees a directory exists, creating
  its parents
* `ensure_file(path, *, create=True)` — guarantees a file exists;
  with `create=False` it acts as a pure precondition
* `ensure_parent_dir(path)` — guarantees the folder a path lives
  in exists and returns the path itself, ready for writing

#### Scanners — look at a directory tree

* `collect_paths(root_dir, *, recursive, include_filter, exclude_filter,
  ignore_names, collect_files, collect_dirs)` — sorted list of files
  and/or directories
* `collect_files(...)` / `collect_dirs(...)` — the same with the type
  flags fixed
* `iter_paths(...)` — lazy, unsorted counterpart; root and options
  are checked when called, not at the first `next()`
* `filter_paths(paths, rule)` — keeps the paths of a collection that
  satisfy a `Rule` or callable
* Safe walking built on `os.scandir`: symlinked directories and
  Windows junctions are never entered, broken symlinks and special
  files are never collected, unreadable subdirectories are skipped,
  and an unreadable, missing or non-directory root is reported
  instead of looking like an empty result

#### Ignore Names

* `DEFAULT_IGNORE_NAMES` — the scanners' default, the union of
  `IGNORE_VCS`, `IGNORE_ENV`, `IGNORE_BUILD`, `IGNORE_IDE`
  and `IGNORE_SYSTEM`
* `IGNORE_GENERIC` — ambiguous output-folder names (`build`, `dist`,
  `site`, `target`, ...), opt-in on purpose
* Names apply to files and directories alike, support glob patterns
  (`*.egg-info`), and match case-insensitively on Windows

#### Rules — `simplibs.path.rules`

* Lexical: `HasSuffix`, `NameIs`, `StemIs`, `ParentNameIs`,
  `IsAbsolutePath`, `IsRelativePath`, `IsHidden`, `IsWithin`,
  `IsValidFilename`
* Filesystem: `PathExists`, `IsFile`, `IsDir`, `IsSymlink`,
  `IsEmptyDir`, `IsEmptyFile`, `IsPathReadable`, `IsPathWritable`
* Every rule returns a strict `bool` without raising, describes itself
  (`describe()`), composes with `&`, `|` and `~`, and produces a
  structured failure card that distinguishes "not a path at all"
  from "a path that fails the rule"

#### Actions — `simplibs.path.actions`

* Transformers: `NormalizePath`, `NormalizeEntryPath`, `RebasePath`,
  `RelativizePath`, `ChangeSuffix`, `MakeUniquePath`
* Ensure: `EnsureDir`, `EnsureFile`, `EnsureParentDir`
* Scanners: `CollectPaths`, `CollectFiles`, `CollectDirs`, `FilterPaths`
* Chainable with `>>`, `&` and `|`, awaitable through `acall`,
  and usable directly behind a `Rule` (`IsDir() >> CollectFiles()`);
  `CollectFiles` and `CollectDirs` are genuinely locked to their type

#### Annotations

* `PathLike` — a non-blank string or a `Path` (a blank string would
  silently mean the current directory)
* `PathPredicate` — a `(Path) -> bool` callable; every `Rule` fits
* `RecursionDepth` — `True`, `False` or a non-negative `int`

#### Package Layout

* `simplibs.path` exports the functions, the ignore-name sets and
  the three annotations directly; `rules` and `actions` are domain
  packages with their own `__all__`

#### Documentation

* Main `README.md` with quick start, package structure and platform notes
* Detailed reference for each part: transformers, checks, ensure,
  scanners, rules, actions and annotations, each function and class
  documented with parameters, return values, raised errors, examples
  and the logic behind it

#### Quality Assurance

* Test suite mirroring the source layout, covering functions, rules,
  actions, helpers, ignore-name sets and error diagnostics
* Contract tests for every rule (`assert_rule_contract`) and action
  (`assert_action`), and for every diagnostic helper
  (`assert_exception_function`)
* Platform-aware tests for symlinks, Windows junctions, permissions
  and the Windows hidden attribute, skipped where the platform or
  privileges do not allow them
* Pipeline tests combining rules and actions, including asynchronous
  execution

#### Dependencies

* `simplibs-exception` — structured exceptions for every diagnostic
* `simplibs-validate` — `@validate_call` on every public function
* `simplibs-rules` — the `Rule` engine behind `simplibs.path.rules`
* `simplibs-actions` — the `Action` abstraction behind
  `simplibs.path.actions`
* `simplibs-types` — annotated building blocks such as non-blank
  strings and positive integers

---

## Legend

* 🔄 **Changed** — modifications to existing functionality
* ✨ **Added** — new features and components
* 🐛 **Fixed** — bug fixes
* 📋 **Improved** — enhancements to existing features
* ⚠️ **Deprecated** — deprecated functionality (not used yet in this
  project)
* 🗑️ **Removed** — removed functionality (not used yet in this project)