import os
import pytest
from simplibs.exception import AccessError, NotFoundError, StateError
from simplibs.path.logic.scanners._helpers import resolve_scan_root


def test_resolve_scan_root_returns_the_normalized_directory(tmp_path) -> None:
    assert resolve_scan_root(tmp_path) == tmp_path.resolve()


def test_resolve_scan_root_normalizes_a_relative_root(tmp_path, monkeypatch) -> None:
    (tmp_path / "sub").mkdir()
    monkeypatch.chdir(tmp_path)
    result = resolve_scan_root("sub/../sub")
    assert result.is_absolute()
    assert result == (tmp_path / "sub").resolve()


def test_resolve_scan_root_accepts_a_string(tmp_path) -> None:
    assert resolve_scan_root(str(tmp_path)) == tmp_path.resolve()


def test_resolve_scan_root_rejects_a_missing_root(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        resolve_scan_root(tmp_path / "missing")


def test_resolve_scan_root_rejects_a_file(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    with pytest.raises(StateError):
        resolve_scan_root(target)


@pytest.mark.skipif(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), reason="Needs POSIX permissions and a non-root user")
def test_resolve_scan_root_rejects_an_unreadable_root(tmp_path) -> None:
    locked = tmp_path / "locked"
    locked.mkdir()
    locked.chmod(0o000)
    try:
        with pytest.raises(AccessError):
            resolve_scan_root(locked)
    finally:
        locked.chmod(0o755)
