import os
import subprocess
from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, ParamError, StateError, ValidationError
from simplibs.rules import Rule
from simplibs.path.logic.scanners import DEFAULT_IGNORE_NAMES, IGNORE_GENERIC, collect_paths


class _IsPython(Rule):
    __slots__ = ()

    def is_valid(self, value) -> bool:
        return value.suffix == ".py"

    def build_exception(self, value, value_name=None, context=None) -> Exception:
        return ValueError("not python")


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("x")
    (root / "b.txt").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "c.py").write_text("x")
    (root / "sub" / "deep").mkdir()
    (root / "sub" / "deep" / "d.md").write_text("x")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("x")
    (root / "__pycache__").mkdir()
    (root / "__pycache__" / "a.pyc").write_text("x")


def _relative(paths, root: Path) -> list[str]:
    return [path.relative_to(root.resolve()).as_posix() for path in paths]


def test_collect_paths_collects_files_by_default(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _relative(collect_paths(tmp_path), tmp_path) == ["a.py", "b.txt", "sub/c.py", "sub/deep/d.md"]


def test_collect_paths_skips_the_default_ignored_names(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _relative(collect_paths(tmp_path), tmp_path)
    assert not any(part in (".git", "__pycache__") for item in result for part in item.split("/"))


def test_collect_paths_can_collect_only_directories(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _relative(collect_paths(tmp_path, collect_files=False, collect_dirs=True), tmp_path) == ["sub", "sub/deep"]


def test_collect_paths_can_collect_files_and_directories(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _relative(collect_paths(tmp_path, collect_dirs=True), tmp_path)
    assert result == ["a.py", "b.txt", "sub", "sub/c.py", "sub/deep", "sub/deep/d.md"]


def test_collect_paths_result_is_sorted_absolute_and_excludes_the_root(tmp_path) -> None:
    _make_tree(tmp_path)
    result = collect_paths(tmp_path, collect_dirs=True)
    assert result == sorted(result)
    assert all(path.is_absolute() for path in result)
    assert tmp_path.resolve() not in result


def test_collect_paths_returns_a_list(tmp_path) -> None:
    assert collect_paths(tmp_path) == []
    assert isinstance(collect_paths(tmp_path), list)


def test_collect_paths_accepts_a_string_root(tmp_path) -> None:
    _make_tree(tmp_path)
    assert len(collect_paths(str(tmp_path))) == 4


@pytest.mark.parametrize(
    "recursive, expected",
    [
        (True, ["a.py", "b.txt", "sub/c.py", "sub/deep/d.md"]),
        (False, ["a.py", "b.txt"]),
        (0, ["a.py", "b.txt"]),
        (1, ["a.py", "b.txt", "sub/c.py"]),
        (2, ["a.py", "b.txt", "sub/c.py", "sub/deep/d.md"]),
    ],
)
def test_collect_paths_respects_the_recursion_depth(tmp_path, recursive, expected) -> None:
    _make_tree(tmp_path)
    assert _relative(collect_paths(tmp_path, recursive=recursive), tmp_path) == expected


def test_collect_paths_include_filter_with_a_lambda(tmp_path) -> None:
    _make_tree(tmp_path)
    result = collect_paths(tmp_path, include_filter=lambda p: p.suffix == ".py")
    assert _relative(result, tmp_path) == ["a.py", "sub/c.py"]


def test_collect_paths_include_filter_with_a_rule(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _relative(collect_paths(tmp_path, include_filter=_IsPython()), tmp_path) == ["a.py", "sub/c.py"]


def test_collect_paths_exclude_filter_with_a_rule(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _relative(collect_paths(tmp_path, exclude_filter=_IsPython()), tmp_path) == ["b.txt", "sub/deep/d.md"]


def test_collect_paths_exclude_wins_over_include(tmp_path) -> None:
    _make_tree(tmp_path)
    result = collect_paths(
        tmp_path,
        include_filter=lambda p: p.suffix == ".py",
        exclude_filter=lambda p: p.name == "c.py",
    )
    assert _relative(result, tmp_path) == ["a.py"]


def test_collect_paths_excluding_a_directory_does_not_hide_its_content(tmp_path) -> None:
    _make_tree(tmp_path)
    result = collect_paths(tmp_path, collect_dirs=True, exclude_filter=lambda p: p.name == "sub")
    assert "sub" not in _relative(result, tmp_path)
    assert "sub/c.py" in _relative(result, tmp_path)


def test_collect_paths_ignore_names_none_ignores_nothing(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _relative(collect_paths(tmp_path, ignore_names=None), tmp_path)
    assert ".git/config" in result and "__pycache__/a.pyc" in result


def test_collect_paths_custom_ignore_names_replace_the_default(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _relative(collect_paths(tmp_path, ignore_names={"sub"}), tmp_path)
    assert result == [".git/config", "__pycache__/a.pyc", "a.py", "b.txt"]


def test_collect_paths_ignore_names_can_extend_the_default(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _relative(collect_paths(tmp_path, ignore_names=DEFAULT_IGNORE_NAMES | {"deep"}), tmp_path)
    assert result == ["a.py", "b.txt", "sub/c.py"]


def test_collect_paths_ignore_names_support_glob_patterns(tmp_path) -> None:
    (tmp_path / "pkg.egg-info").mkdir()
    (tmp_path / "pkg.egg-info" / "PKG-INFO").write_text("x")
    (tmp_path / "keep.py").write_text("x")
    assert _relative(collect_paths(tmp_path), tmp_path) == ["keep.py"]


def test_collect_paths_ignore_names_apply_to_files(tmp_path) -> None:
    (tmp_path / ".DS_Store").write_text("x")
    (tmp_path / "Thumbs.db").write_text("x")
    (tmp_path / ".env").write_text("SECRET=1")
    (tmp_path / "keep.py").write_text("x")
    assert _relative(collect_paths(tmp_path), tmp_path) == ["keep.py"]


def test_collect_paths_ambiguous_folders_are_collected_by_default(tmp_path) -> None:
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "tool.py").write_text("x")
    (tmp_path / "src").mkdir()
    (tmp_path / "src" / "site").mkdir()
    (tmp_path / "src" / "site" / "page.py").write_text("x")
    result = _relative(collect_paths(tmp_path), tmp_path)
    assert result == ["build/tool.py", "src/site/page.py"]


def test_collect_paths_ambiguous_folders_can_be_ignored_explicitly(tmp_path) -> None:
    (tmp_path / "build").mkdir()
    (tmp_path / "build" / "tool.py").write_text("x")
    (tmp_path / "keep.py").write_text("x")
    result = collect_paths(tmp_path, ignore_names=DEFAULT_IGNORE_NAMES | IGNORE_GENERIC)
    assert _relative(result, tmp_path) == ["keep.py"]


def test_collect_paths_does_not_enter_a_symlinked_directory(tmp_path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (real / "inside.txt").write_text("x")
    root = tmp_path / "root"
    root.mkdir()
    try:
        (root / "link").symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert collect_paths(root) == []
    assert _relative(collect_paths(root, collect_files=False, collect_dirs=True), root) == ["link"]


def test_collect_paths_does_not_collect_a_broken_symlink(tmp_path) -> None:
    (tmp_path / "keep.txt").write_text("x")
    try:
        (tmp_path / "dangling").symlink_to(tmp_path / "nowhere")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert _relative(collect_paths(tmp_path), tmp_path) == ["keep.txt"]
    assert collect_paths(tmp_path, collect_files=False, collect_dirs=True) == []


def test_collect_paths_collects_a_file_symlink_as_a_file(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (tmp_path / "real.txt").write_text("x")
    try:
        (root / "link.txt").symlink_to(tmp_path / "real.txt")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert _relative(collect_paths(root), root) == ["link.txt"]


@pytest.mark.skipif(os.name != "nt", reason="Junctions exist on Windows only")
def test_collect_paths_does_not_follow_a_windows_junction_cycle(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (root / "a.txt").write_text("x")
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(root / "loop"), str(tmp_path)],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("Creating a junction failed here.")
    assert _relative(collect_paths(root), root) == ["a.txt"]


def test_collect_paths_rejects_a_missing_root(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        collect_paths(tmp_path / "missing")


def test_collect_paths_rejects_a_file_as_root(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    with pytest.raises(StateError):
        collect_paths(target)


def test_collect_paths_rejects_both_flags_off(tmp_path) -> None:
    with pytest.raises(ParamError):
        collect_paths(tmp_path, collect_files=False, collect_dirs=False)


def test_collect_paths_rejects_a_bare_string_for_ignore_names(tmp_path) -> None:
    with pytest.raises(ParamError):
        collect_paths(tmp_path, ignore_names=".git")


def test_collect_paths_rejects_a_generator_for_ignore_names_without_consuming_it(tmp_path) -> None:
    names = (name for name in (".git", "venv"))
    with pytest.raises(ValidationError):
        collect_paths(tmp_path, ignore_names=names)
    assert next(names) == ".git"


@pytest.mark.parametrize("bad_recursive", [-1, "yes", 1.5, None])
def test_collect_paths_rejects_an_invalid_recursion_depth(tmp_path, bad_recursive) -> None:
    with pytest.raises(ValidationError):
        collect_paths(tmp_path, recursive=bad_recursive)


@pytest.mark.parametrize("bad_filter", [42, "suffix", Path("a")])
def test_collect_paths_rejects_a_non_callable_filter(tmp_path, bad_filter) -> None:
    with pytest.raises(ValidationError):
        collect_paths(tmp_path, include_filter=bad_filter)
    with pytest.raises(ValidationError):
        collect_paths(tmp_path, exclude_filter=bad_filter)


@pytest.mark.parametrize("value", ["", "   ", None, 5])
def test_collect_paths_rejects_an_invalid_root(value) -> None:
    with pytest.raises(ValidationError):
        collect_paths(value)
