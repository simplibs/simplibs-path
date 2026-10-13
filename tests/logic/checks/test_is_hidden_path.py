import os
from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.path.logic.checks import is_hidden_path


@pytest.mark.parametrize("path", [".git", "dir/.env", Path(".hidden"), "/abs/dir/.config", "~/.bashrc"])
def test_is_hidden_path_true_for_dot_names(path) -> None:
    assert is_hidden_path(path) is True


@pytest.mark.parametrize("path", ["file.txt", "dir/file", ".", "..", "dir/.", "dir/..", "/abs/.hidden_dir/file.txt"])
def test_is_hidden_path_false_otherwise(path) -> None:
    """Only the final name counts; '.' and '..' are never hidden."""
    assert is_hidden_path(path) is False


def test_is_hidden_path_never_touches_the_disk_by_default(tmp_path) -> None:
    """A missing path is judged by its name alone."""
    assert is_hidden_path(tmp_path / "nowhere" / ".x") is True


def test_is_hidden_path_check_attributes_false_for_a_missing_path(tmp_path) -> None:
    assert is_hidden_path(tmp_path / "missing.txt", check_attributes=True) is False


def test_is_hidden_path_check_attributes_has_no_effect_for_ordinary_files(tmp_path) -> None:
    target = tmp_path / "plain.txt"
    target.write_text("x")
    assert is_hidden_path(target, check_attributes=True) is False


@pytest.mark.skipif(os.name != "nt", reason="The hidden attribute exists on Windows only")
def test_is_hidden_path_detects_the_windows_hidden_attribute(tmp_path) -> None:
    import ctypes
    target = tmp_path / "visible_name.txt"
    target.write_text("x")
    assert ctypes.windll.kernel32.SetFileAttributesW(str(target), 0x2)
    assert is_hidden_path(target) is False
    assert is_hidden_path(target, check_attributes=True) is True


@pytest.mark.parametrize("value", ["", "  ", None, 5])
def test_is_hidden_path_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        is_hidden_path(value)


def test_is_hidden_path_returns_false_for_a_null_byte() -> None:
    """A string that cannot be a path is simply not hidden."""
    assert is_hidden_path("a\0.b") is False


def test_is_hidden_path_validation_can_be_bypassed() -> None:
    """With the reserved bypass switch, a non-path value answers False instead of failing validation."""
    assert is_hidden_path(42, _validate_call=False) is False
