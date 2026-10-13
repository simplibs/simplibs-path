# 📐 `rules` — Rules for Paths

The `rules` package holds `Rule` classes for paths. Every one is a real `Rule` from
[`simplibs-rules`](https://pypi.org/project/simplibs-rules/) — a thin wrapper over a
function in [`logic`](logic/README_PATH_CHECKS.md) or a single `pathlib` call — so it
composes with `&`, `|` and `~`, describes itself, and explains its failures.

```python
from simplibs.path.rules import HasSuffix, IsFile, IsHidden, IsWithin
```

Rules are **not** exported from `simplibs.path` itself — they are a domain of their own,
imported through `simplibs.path.rules`, which defines `__all__`.

## Where rules are used

```python
# 1. As scanner filters
collect_files("project", include_filter=IsFile() & HasSuffix(".py") & ~IsHidden())

# 2. As validation of your own function arguments (simplibs-validate)
ExistingDir = validated_type(Path, IsDir())

@validate_call
def process(source: ExistingDir) -> None: ...

# 3. As pipeline gates (simplibs-actions) — a rule becomes a pass-through guard step
pipeline = IsDir() >> CollectFiles() >> FilterPaths(rule=~IsHidden())

# 4. Directly
IsWithin("out").is_valid("out/reports/a.md")        # -> True
IsWithin("out").validate("out/../secret.txt")       # raises a ValidationError card
```

## What every rule here guarantees

* **`is_valid` returns a strict `bool` and never raises.** Anything that cannot be a path
  — `None`, a number, a blank string, a string with a null byte — and anything the
  operating system refuses simply fails the rule.
* **`describe()` is a short noun phrase** that containers compose into readable text:
  `(IsFile() & HasSuffix(".py") & ~IsHidden()).describe()` →
  `"existing file & suffix '.py' & not hidden path"`.
* **The failure card says what is wrong.** A value that is not a path at all gives a
  `TypeError` card (`Value 5 of type 'int' is not a string or Path.`); a blank string or
  one with a null byte gives a `ValueError` card; a usable path that fails the rule's own
  condition gives that rule's `problem` / `how_to_fix`. The `error_name` follows the
  rules library convention `<NAME>_ERROR` (`IS_FILE_ERROR`, `HAS_SUFFIX_ERROR`, ...).
* **Constructor mistakes are `ParamError`s**, raised when the rule is built, not when it
  is first used (a suffix without a dot, a non-callable operand, a blank root, a non-bool
  option). Options are keyword-only where a bare positional value would read as a mystery
  (`IsHidden(check_attributes=True)`, never `IsHidden(True)`).
* **`~Rule()` is not "the same rule, inverted" for non-paths.** `~IsDir()` also accepts
  `None` and `5`, because they are not directories. Where the distinction matters
  (`IsRelativePath` vs `~IsAbsolutePath()`), the dedicated rule requires a real path first.

## Two groups

| Group         | What it does                                           | Cost                                      |
|---------------|--------------------------------------------------------|-------------------------------------------|
| `lexical/`    | Judges a path by its **text**.                         | No disk access — safe per entry in a scan. |
| `filesystem/` | Asks the **disk** about the path.                      | One or two syscalls per call.             |

A rule given a leading `~` expands it (`to_path`), but never resolves symlinks or touches
the disk unless it is a `filesystem/` rule (or `IsWithin` with `resolve_symlinks=True`).

---

## 🧭 Table of Contents

**Lexical** — judge a path by its text

* [`HasSuffix`](#hassuffix)
* [`NameIs`](#nameis) · [`StemIs`](#stemis) · [`ParentNameIs`](#parentnameis)
* [`IsAbsolutePath`](#isabsolutepath) · [`IsRelativePath`](#isrelativepath)
* [`IsHidden`](#ishidden)
* [`IsWithin`](#iswithin)
* [`IsValidFilename`](#isvalidfilename)

**Filesystem** — ask the disk

* [`PathExists`](#pathexists)
* [`IsFile`](#isfile) · [`IsDir`](#isdir) · [`IsSymlink`](#issymlink)
* [`IsEmptyDir`](#isemptydir) · [`IsEmptyFile`](#isemptyfile)
* [`IsPathReadable`](#ispathreadable) · [`IsPathWritable`](#ispathwritable)

[⬅️ Back to main README](../README.md#-rules--rules-for-paths)

---

# Lexical rules

### `HasSuffix`

The name must end with one of the given suffixes — the most common filter of an
extraction pipeline.

**Parameters:**

* `*suffixes` (*str*): One or more suffixes — `""` or a dot plus at least one character
  (`".py"`, `".tar.gz"`), no separators. At least one is required.
* `ignore_case` (*bool*, keyword-only, default `True`): Compare case-insensitively.

**`describe()`:** `"suffix '.py'"` · `"suffix one of '.py', '.md'"` ·
`"suffix '.py' (case-sensitive)"`.

**Example usage:**

```python
HasSuffix(".py").is_valid("src/a.py")            # -> True
HasSuffix(".py", ".md").is_valid("README.MD")    # -> True   (case-insensitive)
HasSuffix(".tar.gz").is_valid("backup.tar.gz")   # -> True   (compound suffix)
HasSuffix("").is_valid("Makefile")               # -> True   ("" means: no suffix at all)
HasSuffix(".py").is_valid(".py")                 # -> False  (a suffix needs a base name)
```

**Notes.** It looks at the **end of the name**, not `Path.suffix`, which is why compound
suffixes work. It is lexical: a *directory* named `pkg.py` matches too — combine with
`IsFile()` when the type matters. `HasSuffix("py")` is a `ParamError` (it would match any
name merely ending in "py"). Error name: `HAS_SUFFIX_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `NameIs`

The path's **final name** (`report.txt`) must satisfy another rule — so the whole
string-rule vocabulary (`StartsWith`, `Regex`, `Contains`, ...) applies to file names
without a path-specific copy of any of it.

**Parameters:**

* `rule` (*Rule | Callable[[str], bool]*): Judges the name as a string. A plain callable is
  wrapped so it can describe itself and explain a failure.

**`describe()`:** `"name: <rule>"` — a compound operand is parenthesized:
`"name: (string containing 'a' | string containing 'b')"`.

**Example usage:**

```python
NameIs(Contains("test_")).is_valid("src/test_app.py")      # -> True
NameIs(Contains("test_")).is_valid("test_dir/app.py")      # -> False  (only the name counts)
NameIs(lambda name: name.startswith("_")).is_valid("a/_x.py")   # -> True
```

**Notes.** On failure the card is the **wrapped rule's own**, about the extracted name and
labelled `<value_name>.name` — so `exc.value` is the name, not the whole path. A
non-callable `rule` is a `ParamError`. Error name for a non-path value: `NAME_IS_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `StemIs`

The final name **without its last suffix** (`report`) must satisfy another rule.

**Parameters:**

* `rule` (*Rule | Callable[[str], bool]*): Judges the stem as a string.

**`describe()`:** `"stem: <rule>"`.

**Example usage:**

```python
StemIs(Contains("draft")).is_valid("notes/draft_1.txt")    # -> True
StemIs(Contains("py")).is_valid("a.py")                    # -> False  (the stem is just "a")
StemIs(Contains("tar")).is_valid("archive.tar.gz")         # -> True   (stem: "archive.tar")
```

**Notes.** `NameIs(Contains("py"))` would match `a.py` because the *extension* contains
"py"; `StemIs` judges only the part before the last suffix. Same failure-card behavior as
`NameIs` (label `<value_name>.stem`). Error name for a non-path value: `STEM_IS_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `ParentNameIs`

The name of the directory **directly containing** the path must satisfy another rule.

**Parameters:**

* `rule` (*Rule | Callable[[str], bool]*): Judges the folder name as a string.

**`describe()`:** `"parent name: <rule>"`.

**Example usage:**

```python
ParentNameIs(Equals("tests")).is_valid("project/tests/test_a.py")   # -> True
ParentNameIs(Equals("tests")).is_valid("tests/unit/test_a.py")      # -> False
```

**Notes.** Only the *directly* containing folder is examined. A bare relative name such as
`a.txt` has an **empty** parent name — the path says nothing about where it lives; paths
produced by the scanners are absolute, so this only arises for hand-written relative
paths. Label `<value_name>.parent name`; error name for a non-path value:
`PARENT_NAME_IS_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `IsAbsolutePath`

The path must be absolute.

**Parameters:** none.

**`describe()`:** `"absolute path"`.

**Example usage:**

```python
IsAbsolutePath().is_valid("/home/me/project")    # -> True   (POSIX)
IsAbsolutePath().is_valid("C:\\Users\\me")       # -> True   (Windows)
IsAbsolutePath().is_valid("src/a.py")            # -> False
IsAbsolutePath().is_valid("~/project")           # -> True   (~ is expanded to the home directory)
```

**Notes.** It follows the platform: `/etc` is absolute on POSIX but **not** on Windows (no
drive). No disk access. Error name: `IS_ABSOLUTE_PATH_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `IsRelativePath`

The path must be relative.

**Parameters:** none.

**`describe()`:** `"relative path"`.

**Example usage:**

```python
IsRelativePath().is_valid("src/a.py")      # -> True
IsRelativePath().is_valid("../x")          # -> True
IsRelativePath().is_valid("/etc")          # -> False  (POSIX)
IsRelativePath().is_valid(None)            # -> False  (a non-path is neither absolute nor relative)
```

**Notes.** Not simply `~IsAbsolutePath()`: that would also accept `None`, `5` and `""`. Error
name: `IS_RELATIVE_PATH_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `IsHidden`

The path's final name starts with a dot (and, optionally, carries the Windows hidden
attribute).

**Parameters:**

* `check_attributes` (*bool*, keyword-only, default `False`): Also count the Windows
  "hidden" file attribute (one `stat` call per path; no effect elsewhere).

**`describe()`:** `"hidden path"`.

**Example usage:**

```python
IsHidden().is_valid(".git")                 # -> True
IsHidden().is_valid("src/.env")             # -> True
IsHidden().is_valid("/home/me/.config/a.json")   # -> False  (only the final name counts)

collect_files("project", exclude_filter=IsHidden())
```

**Notes.** Mostly used negated (`~IsHidden()`). Delegates to
[`is_hidden_path`](logic/README_PATH_CHECKS.md#is_hidden_path). Error name:
`IS_HIDDEN_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `IsWithin`

The path must lie **inside** the given root directory — the path-traversal guard as a rule.

**Parameters:**

* `root` (*str | Path*): The directory the path must be inside. Not normalized at
  construction — a relative root means "relative to the working directory at evaluation
  time". Blank or non-path roots are a `ParamError`.
* `resolve_symlinks` (*bool*, keyword-only, default `True`): Resolve symlinks and `..`
  before comparing.
* `allow_equal` (*bool*, keyword-only, default `True`): Count a path equal to the root as inside.

**`describe()`:** `"path within '<root>'"`.

**Example usage:**

```python
gate = IsWithin("out")
gate.is_valid("out/reports/a.md")        # -> True
gate.is_valid("out/../secret.txt")       # -> False
gate.validate("out2/a.md")               # raises — "out2" is not inside "out"

IsWithin("out") >> WriteStep()           # as a pipeline gate on a computed path
```

**Notes.** Delegates to [`is_within`](logic/README_PATH_CHECKS.md#is_within); the
defaults are the safe ones, and a filter over already-normalized scanner output can pass
`resolve_symlinks=False` to skip the syscalls. Error name: `IS_WITHIN_ERROR`.

[▲ Back to top](#-table-of-contents)

---

### `IsValidFilename`

A string must be a usable file name; for a `Path`, its **final name** must be.

**Parameters:**

* `portable` (*bool*, keyword-only, default `True`): Valid on both Windows and POSIX.
  `False` applies only the current operating system's rules.

**`describe()`:** `"portable file name"` · `"file name valid on this OS"`.

**Example usage:**

```python
IsValidFilename().is_valid("report.md")              # -> True
IsValidFilename().is_valid("dir/report.md")          # -> False  (a str is a name — "/" is a separator)
IsValidFilename().is_valid(Path("dir/report.md"))    # -> True   (a Path is judged by its final name)
IsValidFilename().validate("what?.md")
# ValidationError: 'what?.md' is not a usable file name (contains the character '?',
#                  which Windows forbids in names).
```

**Notes.** Delegates to `is_valid_filename`; the reason in the card comes from the same
`find_filename_problem` the function uses, so the rule can never reject for one reason and
explain with another. See [`is_valid_filename`](logic/README_PATH_CHECKS.md#is_valid_filename)
for the rules. Error name: `IS_VALID_FILENAME_ERROR`.

[▲ Back to top](#-table-of-contents)

---

# Filesystem rules

Each of these returns `False` — never an exception — for a missing path, a permission
problem, a bad name or a path behind a folder you may not enter. (`Path.is_file()` itself
re-raises `PermissionError` there; the rules do not.)

### `PathExists`

Something exists at the path.

**`describe()`:** `"existing path"`. **Error name:** `PATH_EXISTS_ERROR`.

```python
PathExists().is_valid("src")            # -> True
PathExists().is_valid("missing.txt")    # -> False
```

Follows symlinks: a **broken** symlink answers `False` (what it points at is missing).

[▲ Back to top](#-table-of-contents)

---

### `IsFile`

An existing regular file — or a symlink to one.

**`describe()`:** `"existing file"`. **Error name:** `IS_FILE_ERROR`.

```python
IsFile().is_valid("src/a.py")      # -> True
IsFile().is_valid("src")           # -> False  (a directory)
collect_paths("project", include_filter=IsFile() & HasSuffix(".py"))
```

[▲ Back to top](#-table-of-contents)

---

### `IsDir`

An existing directory — or a symlink to one.

**`describe()`:** `"existing directory"`. **Error name:** `IS_DIR_ERROR`.

```python
IsDir().is_valid("src")            # -> True
pipeline = IsDir() >> CollectFiles()    # the natural head of a pipeline
```

[▲ Back to top](#-table-of-contents)

---

### `IsSymlink`

The path **itself** is a symbolic link, working or broken.

**`describe()`:** `"symbolic link"`. **Error name:** `IS_SYMLINK_ERROR`.

```python
IsSymlink().is_valid("link_to_data")       # -> True
IsSymlink().is_valid("dangling_link")      # -> True   (PathExists would say False)
```

The only rule that looks at the *link* rather than its target. Detecting symlinks needs no
privileges on Windows (creating them does). Directory junctions are not symlinks and answer
`False`.

[▲ Back to top](#-table-of-contents)

---

### `IsEmptyDir`

An existing directory with no entries.

**`describe()`:** `"empty directory"`. **Error name:** `IS_EMPTY_DIR_ERROR`.

```python
IsEmptyDir().is_valid("out")        # -> True
validate(output_dir, IsEmptyDir())  # "only write into an empty folder"
```

Delegates to [`is_empty_dir`](logic/README_PATH_CHECKS.md#is_empty_dir): an unlistable
directory is *not* reported empty.

[▲ Back to top](#-table-of-contents)

---

### `IsEmptyFile`

An existing regular file of size zero.

**`describe()`:** `"empty file"`. **Error name:** `IS_EMPTY_FILE_ERROR`.

```python
collect_files("project", exclude_filter=IsEmptyFile())
```

It is the *size*, not the content: a file holding a single space is not empty.

[▲ Back to top](#-table-of-contents)

---

### `IsPathReadable`

A file that can be read, or a directory that can be listed.

**`describe()`:** `"readable path"`. **Error name:** `IS_PATH_READABLE_ERROR`.

```python
validate(source, IsPathReadable())
```

Delegates to [`is_path_readable`](logic/README_PATH_CHECKS.md#is_path_readable): it
actually opens the file, so a permission problem is reported as *unreadable*, not as missing.

[▲ Back to top](#-table-of-contents)

---

### `IsPathWritable`

Could be written to **now**, with nothing created or changed — an existing file or
directory, or a new file in a writable directory.

**`describe()`:** `"writable path"`. **Error name:** `IS_PATH_WRITABLE_ERROR`.

```python
IsPathWritable().is_valid("out/new_report.md")     # -> True  (out/ exists and accepts files)
IsPathWritable().is_valid("missing/x.md")          # -> False (no such folder — none is created)
```

Delegates to [`is_path_writable`](logic/README_PATH_CHECKS.md#is_path_writable). An
earlier version created an empty file for a path that did not exist; it is now a pure
check. A missing parent folder is `False` — creating it is `ensure_parent_dir`'s job.

[▲ Back to top](#-table-of-contents)

---

[⬅️ Back to main README](../README.md#-rules--rules-for-paths)
