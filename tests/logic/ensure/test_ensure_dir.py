import os
from pathlib import Path
import pytest
from simplibs.exception import AccessError, StateError, ValidationError
from simplibs.path.logic.ensure import ensure_dir


def _is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def test_ensure_dir_creates_a_missing_directory(tmp_path) -> None:
    target = tmp_path / "new"
    result = ensure_dir(target)
    assert target.is_dir()
    assert result == target.resolve()


def test_ensure_dir_creates_missing_parents(tmp_path) -> None:
    target = tmp_path / "a" / "b" / "c"
    ensure_dir(target)
    assert target.is_dir()


def test_ensure_dir_keeps_an_existing_directory_untouched(tmp_path) -> None:
    (tmp_path / "keep.txt").write_text("content")
    result = ensure_dir(tmp_path)
    assert result == tmp_path.resolve()
    assert (tmp_path / "keep.txt").read_text() == "content"


def test_ensure_dir_is_idempotent(tmp_path) -> None:
    target = tmp_path / "x" / "y"
    assert ensure_dir(target) == ensure_dir(target)


def test_ensure_dir_returns_an_absolute_normalized_path(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = ensure_dir("rel/../out")
    assert result.is_absolute()
    assert result == (tmp_path / "out").resolve()
    assert result.is_dir()


def test_ensure_dir_accepts_a_string(tmp_path) -> None:
    assert ensure_dir(str(tmp_path / "from_string")).is_dir()


def test_ensure_dir_rejects_a_path_occupied_by_a_file(tmp_path) -> None:
    blocker = tmp_path / "file.txt"
    blocker.write_text("x")
    with pytest.raises(StateError):
        ensure_dir(blocker)


def test_ensure_dir_fails_when_a_parent_is_a_file(tmp_path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    with pytest.raises((AccessError, StateError)):
        ensure_dir(blocker / "sub" / "leaf")


def test_ensure_dir_follows_a_dangling_symlink_to_its_target(tmp_path) -> None:
    link = tmp_path / "link"
    try:
        link.symlink_to(tmp_path / "real_target", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    result = ensure_dir(link)
    assert result == (tmp_path / "real_target").resolve()
    assert (tmp_path / "real_target").is_dir()


@pytest.mark.skipif(os.name == "nt" or _is_root(), reason="Needs POSIX directory permissions and a non-root user")
def test_ensure_dir_reports_missing_permissions(tmp_path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o555)
    try:
        with pytest.raises(AccessError):
            ensure_dir(locked / "child")
    finally:
        locked.chmod(0o755)


@pytest.mark.parametrize("value", ["", "   ", None, 5, b"x"])
def test_ensure_dir_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        ensure_dir(value)


def test_ensure_dir_rejects_a_null_byte() -> None:
    with pytest.raises(AccessError):
        ensure_dir("bad\0dir")
