import os
from pathlib import Path
import pytest
from simplibs.exception import AccessError, ValidationError
from simplibs.path.logic.transformers import normalize_path


def _symlink_or_skip(link: Path, target: Path) -> None:
    """Create a directory symlink, or skip the test where that is not permitted."""
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")


def test_normalize_path_returns_absolute_path(tmp_path, monkeypatch) -> None:
    """A relative path becomes absolute, relative to the working directory."""
    monkeypatch.chdir(tmp_path)
    result = normalize_path("some/dir")
    assert result.is_absolute()
    assert result == (tmp_path / "some" / "dir").resolve()


def test_normalize_path_does_not_require_existence(tmp_path) -> None:
    """A path that does not exist is normalized without error."""
    target = tmp_path / "missing" / "deep" / "file.txt"
    assert normalize_path(target) == target.resolve()


def test_normalize_path_collapses_parent_references(tmp_path) -> None:
    """`..` and `.` components are collapsed."""
    messy = tmp_path / "a" / ".." / "b" / "." / "c"
    assert normalize_path(messy) == (tmp_path / "b" / "c").resolve()


def test_normalize_path_expands_user() -> None:
    """A leading `~` becomes the home directory."""
    assert normalize_path("~") == Path.home().resolve()


def test_normalize_path_accepts_path_instances(tmp_path) -> None:
    """A Path instance is accepted just like a string."""
    assert normalize_path(tmp_path) == tmp_path.resolve()


def test_normalize_path_is_idempotent(tmp_path) -> None:
    """Normalizing an already normalized path changes nothing."""
    once = normalize_path(tmp_path / "x" / "..")
    assert normalize_path(once) == once


@pytest.mark.parametrize("value", ["", "   ", None, 42, b"x"])
def test_normalize_path_rejects_invalid_input(value) -> None:
    """Blank strings and non-path types are rejected by the PathLike annotation."""
    with pytest.raises(ValidationError):
        normalize_path(value)


@pytest.mark.parametrize("resolve_symlinks", [True, False])
def test_normalize_path_reports_null_byte(resolve_symlinks) -> None:
    """A null byte raises the same AccessError card in both modes."""
    with pytest.raises(AccessError):
        normalize_path("bad\0path", resolve_symlinks=resolve_symlinks)


def test_normalize_path_follows_symlinks_by_default(tmp_path) -> None:
    """With the default, a symlinked directory resolves to its real location."""
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_or_skip(link, real)
    assert normalize_path(link / "file.txt") == (real / "file.txt").resolve()


def test_normalize_path_can_keep_symlinks(tmp_path) -> None:
    """With resolve_symlinks=False, the symlink stays in the result."""
    real = tmp_path / "real"
    real.mkdir()
    link = tmp_path / "link"
    _symlink_or_skip(link, real)
    result = normalize_path(link / "file.txt", resolve_symlinks=False)
    assert result == Path(os.path.abspath(link / "file.txt"))
    assert "link" in result.parts


def test_normalize_path_lexical_mode_collapses_parent_references(tmp_path) -> None:
    """The lexical mode still collapses `..` — just without asking the disk."""
    messy = tmp_path / "a" / ".." / "b"
    assert normalize_path(messy, resolve_symlinks=False) == Path(os.path.abspath(tmp_path / "b"))
