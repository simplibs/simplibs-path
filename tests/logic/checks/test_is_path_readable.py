import os
import pytest
from simplibs.exception import ValidationError
from simplibs.path.logic.checks import is_path_readable


def _is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def test_is_path_readable_true_for_a_file(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    assert is_path_readable(target) is True


def test_is_path_readable_true_for_an_empty_file(tmp_path) -> None:
    target = tmp_path / "empty.txt"
    target.write_text("")
    assert is_path_readable(target) is True


def test_is_path_readable_true_for_a_directory(tmp_path) -> None:
    assert is_path_readable(tmp_path) is True


def test_is_path_readable_false_for_a_missing_path(tmp_path) -> None:
    assert is_path_readable(tmp_path / "missing.txt") is False


def test_is_path_readable_does_not_modify_the_file(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_bytes(b"content")
    is_path_readable(target)
    assert target.read_bytes() == b"content"


def test_is_path_readable_false_for_a_broken_symlink(tmp_path) -> None:
    link = tmp_path / "dangling"
    try:
        link.symlink_to(tmp_path / "nowhere")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert is_path_readable(link) is False


@pytest.mark.skipif(os.name == "nt" or _is_root(), reason="Needs POSIX permissions and a non-root user")
def test_is_path_readable_false_for_a_file_without_read_permission(tmp_path) -> None:
    target = tmp_path / "secret.txt"
    target.write_text("x")
    target.chmod(0o000)
    try:
        assert is_path_readable(target) is False
    finally:
        target.chmod(0o600)


@pytest.mark.parametrize("value", ["", "   ", None, 5, b"x"])
def test_is_path_readable_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        is_path_readable(value)


def test_is_path_readable_false_for_a_null_byte() -> None:
    assert is_path_readable("a\0b") is False
