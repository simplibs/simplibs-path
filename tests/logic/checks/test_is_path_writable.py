import os
import stat
import pytest
from simplibs.exception import ValidationError
from simplibs.path.logic.checks import is_path_writable


def _is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def test_is_path_writable_true_for_an_existing_file(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    assert is_path_writable(target) is True


def test_is_path_writable_does_not_change_an_existing_file(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_bytes(b"content")
    is_path_writable(target)
    assert target.read_bytes() == b"content"


def test_is_path_writable_true_for_an_existing_directory(tmp_path) -> None:
    assert is_path_writable(tmp_path) is True


def test_is_path_writable_leaves_a_directory_untouched(tmp_path) -> None:
    is_path_writable(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_is_path_writable_true_for_a_new_file_in_an_existing_directory(tmp_path) -> None:
    assert is_path_writable(tmp_path / "new.txt") is True


def test_is_path_writable_does_not_create_the_missing_file(tmp_path) -> None:
    """The old implementation left an empty file behind — this must not."""
    is_path_writable(tmp_path / "new.txt")
    assert not (tmp_path / "new.txt").exists()
    assert list(tmp_path.iterdir()) == []


def test_is_path_writable_false_when_the_parent_directory_is_missing(tmp_path) -> None:
    assert is_path_writable(tmp_path / "missing" / "new.txt") is False
    assert not (tmp_path / "missing").exists()


def test_is_path_writable_false_when_the_parent_is_a_file(tmp_path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    assert is_path_writable(blocker / "new.txt") is False


def test_is_path_writable_false_for_a_broken_symlink(tmp_path) -> None:
    link = tmp_path / "dangling"
    try:
        link.symlink_to(tmp_path / "nowhere")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert is_path_writable(link) is False


@pytest.mark.skipif(_is_root(), reason="Root ignores file permissions")
def test_is_path_writable_false_for_a_read_only_file(tmp_path) -> None:
    target = tmp_path / "locked.txt"
    target.write_text("x")
    target.chmod(stat.S_IREAD)
    try:
        assert is_path_writable(target) is False
    finally:
        target.chmod(stat.S_IWRITE | stat.S_IREAD)


@pytest.mark.skipif(os.name == "nt" or _is_root(), reason="Needs POSIX directory permissions and a non-root user")
def test_is_path_writable_false_for_a_read_only_directory(tmp_path) -> None:
    target = tmp_path / "locked_dir"
    target.mkdir()
    target.chmod(0o555)
    try:
        assert is_path_writable(target) is False
        assert is_path_writable(target / "new.txt") is False
    finally:
        target.chmod(0o755)


@pytest.mark.parametrize("value", ["", "   ", None, 5, b"x"])
def test_is_path_writable_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        is_path_writable(value)


def test_is_path_writable_false_for_a_null_byte() -> None:
    assert is_path_writable("a\0b") is False
