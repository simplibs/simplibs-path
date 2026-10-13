from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.path.logic.transformers import relativize_path


def test_relativize_path_returns_part_below_root(tmp_path) -> None:
    """The result is the path as seen from inside the root."""
    assert relativize_path(tmp_path / "src" / "a.py", root=tmp_path) == Path("src/a.py")


def test_relativize_path_same_path_is_dot(tmp_path) -> None:
    """A path equal to its root is the current directory."""
    assert relativize_path(tmp_path, root=tmp_path) == Path(".")


def test_relativize_path_normalizes_both_sides(tmp_path) -> None:
    """Parent references on either side do not break the comparison."""
    messy_path = tmp_path / "x" / ".." / "src" / "a.py"
    messy_root = tmp_path / "y" / ".."
    assert relativize_path(messy_path, root=messy_root) == Path("src/a.py")


def test_relativize_path_works_for_missing_paths(tmp_path) -> None:
    """Neither path has to exist."""
    assert relativize_path(tmp_path / "no" / "such", root=tmp_path / "no") == Path("such")


def test_relativize_path_rejects_path_outside_root(tmp_path) -> None:
    """A path that is not inside the root is a ParamError, not a bare ValueError."""
    with pytest.raises(ParamError):
        relativize_path(tmp_path / "other" / "a.py", root=tmp_path / "src")


def test_relativize_path_sibling_with_common_prefix_is_outside(tmp_path) -> None:
    """'src2' is not inside 'src' even though the names share a prefix."""
    with pytest.raises(ParamError):
        relativize_path(tmp_path / "src2" / "a.py", root=tmp_path / "src")


@pytest.mark.parametrize("value", ["", None, 3])
def test_relativize_path_rejects_invalid_input(tmp_path, value) -> None:
    """Invalid path or root values are rejected by the PathLike annotation."""
    with pytest.raises(ValidationError):
        relativize_path(value, root=tmp_path)
    with pytest.raises(ValidationError):
        relativize_path(tmp_path, root=value)
