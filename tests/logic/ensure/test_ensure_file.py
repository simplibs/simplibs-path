import os
import pytest
from simplibs.exception import AccessError, NotFoundError, StateError, ValidationError
from simplibs.path.logic.ensure import ensure_file


def _is_root() -> bool:
    return hasattr(os, "geteuid") and os.geteuid() == 0


def test_ensure_file_creates_a_missing_empty_file(tmp_path) -> None:
    target = tmp_path / "new.txt"
    result = ensure_file(target)
    assert target.is_file()
    assert target.stat().st_size == 0
    assert result == target.resolve()


def test_ensure_file_creates_missing_parent_directories(tmp_path) -> None:
    target = tmp_path / "a" / "b" / "new.txt"
    ensure_file(target)
    assert target.is_file()


def test_ensure_file_keeps_the_content_of_an_existing_file(tmp_path) -> None:
    target = tmp_path / "keep.txt"
    target.write_text("content")
    result = ensure_file(target)
    assert result == target.resolve()
    assert target.read_text() == "content"


def test_ensure_file_is_idempotent(tmp_path) -> None:
    target = tmp_path / "x.txt"
    assert ensure_file(target) == ensure_file(target)


def test_ensure_file_without_create_accepts_an_existing_file(tmp_path) -> None:
    target = tmp_path / "there.txt"
    target.write_text("x")
    assert ensure_file(target, create=False) == target.resolve()


def test_ensure_file_without_create_raises_for_a_missing_file(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        ensure_file(tmp_path / "missing.txt", create=False)


def test_ensure_file_without_create_creates_nothing(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        ensure_file(tmp_path / "sub" / "missing.txt", create=False)
    assert list(tmp_path.iterdir()) == []


def test_ensure_file_rejects_a_path_occupied_by_a_directory(tmp_path) -> None:
    with pytest.raises(StateError):
        ensure_file(tmp_path)


def test_ensure_file_names_a_file_in_the_parent_chain(tmp_path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    with pytest.raises(StateError):
        ensure_file(blocker / "new.txt")


@pytest.mark.skipif(os.name == "nt" or _is_root(), reason="Needs POSIX directory permissions and a non-root user")
def test_ensure_file_reports_missing_permissions(tmp_path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o555)
    try:
        with pytest.raises(AccessError):
            ensure_file(locked / "new.txt")
    finally:
        locked.chmod(0o755)


@pytest.mark.parametrize("value", ["", "   ", None, 5])
def test_ensure_file_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        ensure_file(value)


def test_ensure_file_rejects_a_non_bool_create_flag(tmp_path) -> None:
    with pytest.raises(ValidationError):
        ensure_file(tmp_path / "x.txt", create="yes")
