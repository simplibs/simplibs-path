import inspect
from pathlib import Path
import pytest
from simplibs.exception import NotFoundError, ValidationError
from simplibs.path.logic.scanners import collect_files, collect_paths


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "b.txt").write_text("x")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("x")


def test_collect_files_collects_only_files(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in collect_files(tmp_path)] == ["a.py", "b.txt"]


def test_collect_files_equals_collect_paths_with_fixed_flags(tmp_path) -> None:
    _make_tree(tmp_path)
    assert collect_files(tmp_path) == collect_paths(tmp_path, collect_files=True, collect_dirs=False)


def test_collect_files_supports_the_shared_options(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in collect_files(tmp_path, recursive=False)] == ["a.py"]
    assert [p.name for p in collect_files(tmp_path, include_filter=lambda p: p.suffix == ".txt")] == ["b.txt"]
    assert [p.name for p in collect_files(tmp_path, exclude_filter=lambda p: p.suffix == ".txt")] == ["a.py"]
    assert "config" in {p.name for p in collect_files(tmp_path, ignore_names=None)}


def test_collect_files_does_not_expose_the_type_flags(tmp_path) -> None:
    parameters = inspect.signature(collect_files).parameters
    assert "collect_files" not in parameters and "collect_dirs" not in parameters
    with pytest.raises(TypeError):
        collect_files(tmp_path, collect_dirs=True)


def test_collect_files_rejects_a_missing_root(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        collect_files(tmp_path / "missing")


@pytest.mark.parametrize("value", ["", None, 5])
def test_collect_files_rejects_an_invalid_root(value) -> None:
    with pytest.raises(ValidationError):
        collect_files(value)
