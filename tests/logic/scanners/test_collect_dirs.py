import inspect
from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, ValidationError
from simplibs.path.logic.scanners import collect_dirs, collect_paths


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "deep").mkdir()
    (root / ".git").mkdir()


def test_collect_dirs_collects_only_directories(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in collect_dirs(tmp_path)] == ["sub", "deep"]


def test_collect_dirs_does_not_include_the_root(tmp_path) -> None:
    _make_tree(tmp_path)
    assert tmp_path.resolve() not in collect_dirs(tmp_path)


def test_collect_dirs_equals_collect_paths_with_fixed_flags(tmp_path) -> None:
    _make_tree(tmp_path)
    assert collect_dirs(tmp_path) == collect_paths(tmp_path, collect_files=False, collect_dirs=True)


def test_collect_dirs_supports_the_shared_options(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in collect_dirs(tmp_path, recursive=False)] == ["sub"]
    assert [p.name for p in collect_dirs(tmp_path, include_filter=lambda p: p.name == "deep")] == ["deep"]
    assert [p.name for p in collect_dirs(tmp_path, exclude_filter=lambda p: p.name == "sub")] == ["deep"]
    assert ".git" in {p.name for p in collect_dirs(tmp_path, ignore_names=None)}


def test_collect_dirs_does_not_expose_the_type_flags(tmp_path) -> None:
    parameters = inspect.signature(collect_dirs).parameters
    assert "collect_files" not in parameters and "collect_dirs" not in parameters
    with pytest.raises(TypeError):
        collect_dirs(tmp_path, collect_files=True)


def test_collect_dirs_returns_an_empty_list_for_a_tree_without_directories(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("x")
    assert collect_dirs(tmp_path) == []


def test_collect_dirs_rejects_a_missing_root(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        collect_dirs(tmp_path / "missing")


@pytest.mark.parametrize("value", ["", None, 5])
def test_collect_dirs_rejects_an_invalid_root(value) -> None:
    with pytest.raises(ValidationError):
        collect_dirs(value)
