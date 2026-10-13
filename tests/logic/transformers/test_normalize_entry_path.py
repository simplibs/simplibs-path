import os
from pathlib import Path

import pytest

from simplibs.exception import AccessError, ParamError, ValidationError
from simplibs.path.logic.transformers import normalize_entry_path


def _symlink_or_skip(link: Path, target: Path) -> None:
    """Create a symlink, or skip the test where that is not permitted."""
    try:
        link.symlink_to(target, target_is_directory=target.is_dir())
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")


def test_normalize_entry_path_returns_absolute_path(tmp_path, monkeypatch) -> None:
    """A relative path becomes absolute, relative to the working directory."""
    monkeypatch.chdir(tmp_path)

    result = normalize_entry_path("some/dir")

    assert result.is_absolute()
    assert result == (tmp_path / "some" / "dir").resolve()


def test_normalize_entry_path_does_not_require_existence(tmp_path) -> None:
    """A missing entry can be normalized without error."""
    target = tmp_path / "missing" / "deep" / "file.txt"

    assert normalize_entry_path(target) == target


def test_normalize_entry_path_collapses_parent_references(tmp_path) -> None:
    """Parent and current-directory references are collapsed."""
    messy = tmp_path / "a" / ".." / "b" / "." / "file.txt"

    assert normalize_entry_path(messy) == tmp_path / "b" / "file.txt"


def test_normalize_entry_path_expands_user() -> None:
    """A leading tilde is expanded to the home directory."""
    assert normalize_entry_path("~") == Path.home().resolve()
    assert normalize_entry_path("~/file.txt") == Path.home().resolve() / "file.txt"


def test_normalize_entry_path_accepts_path_instances(tmp_path) -> None:
    """A Path instance is accepted just like a string."""
    target = tmp_path / "file.txt"

    assert normalize_entry_path(target) == target


def test_normalize_entry_path_is_idempotent(tmp_path) -> None:
    """Normalizing an already normalized entry changes nothing."""
    once = normalize_entry_path(tmp_path / "folder" / ".." / "file.txt")

    assert normalize_entry_path(once) == once


@pytest.mark.parametrize("value", ["", "   ", None, 42, b"x"])
def test_normalize_entry_path_rejects_invalid_input(value) -> None:
    """Blank strings and non-path types are rejected by PathLike."""
    with pytest.raises(ValidationError):
        normalize_entry_path(value)


def test_normalize_entry_path_rejects_filesystem_root(tmp_path) -> None:
    """A filesystem root has no final name and cannot represent an entry."""
    with pytest.raises(ParamError):
        normalize_entry_path(tmp_path.anchor)


def test_normalize_entry_path_reports_null_byte() -> None:
    """A null byte raises AccessError during normalization."""
    with pytest.raises(AccessError):
        normalize_entry_path("bad\0path")


def test_normalize_entry_path_resolves_symlinked_parent(tmp_path) -> None:
    """A symlink in the directory part is resolved."""
    real = tmp_path / "real"
    real.mkdir()

    link = tmp_path / "link"
    _symlink_or_skip(link, real)

    result = normalize_entry_path(link / "file.txt")

    assert result == real / "file.txt"
    assert "link" not in result.parts


def test_normalize_entry_path_preserves_final_symlink(tmp_path) -> None:
    """A final symlink is preserved instead of resolving its target."""
    target = tmp_path / "target.txt"
    target.write_text("content")

    link = tmp_path / "link.txt"
    _symlink_or_skip(link, target)

    result = normalize_entry_path(link)

    assert result == link
    assert result.is_symlink()
    assert result.resolve() == target.resolve()


def test_normalize_entry_path_preserves_dangling_symlink(tmp_path) -> None:
    """A symlink to a missing target remains an entry under its own name."""
    link = tmp_path / "dangling.txt"
    _symlink_or_skip(link, tmp_path / "missing.txt")

    result = normalize_entry_path(link)

    assert result == link
    assert result.is_symlink()
    assert not result.exists()


def test_normalize_entry_path_preserves_final_name_through_parent_symlink(
    tmp_path,
) -> None:
    """The parent is resolved while the final entry name stays unchanged."""
    real = tmp_path / "real"
    real.mkdir()

    link = tmp_path / "link"
    _symlink_or_skip(link, real)

    target = link / "entry.txt"
    result = normalize_entry_path(target)

    assert result == real / "entry.txt"
    assert result.name == "entry.txt"


def test_normalize_entry_path_lexical_parent_collapses_before_resolution(
    tmp_path,
) -> None:
    """Parent references are collapsed before resolving the directory."""
    real = tmp_path / "real"
    real.mkdir()

    link = tmp_path / "link"
    _symlink_or_skip(link, real)

    target = link / ".." / "link" / "entry.txt"
    result = normalize_entry_path(target)

    assert result == real / "entry.txt"


def test_normalize_entry_path_keeps_final_name_case(tmp_path) -> None:
    """The final name is retained as written."""
    target = tmp_path / "MiXeD_Name.TXT"

    assert normalize_entry_path(target).name == "MiXeD_Name.TXT"


def test_normalize_entry_path_does_not_follow_final_symlink_by_default(
    tmp_path,
) -> None:
    """The default behavior preserves a symlink in the final position."""
    target = tmp_path / "target"
    target.mkdir()

    link = tmp_path / "link"
    _symlink_or_skip(link, target)

    result = normalize_entry_path(link)

    assert result == link
    assert result.is_symlink()


def test_normalize_entry_path_resolves_real_parent_for_missing_entry(
    tmp_path,
) -> None:
    """The parent is canonicalized even when the entry does not exist."""
    real = tmp_path / "real"
    real.mkdir()

    link = tmp_path / "link"
    _symlink_or_skip(link, real)

    result = normalize_entry_path(link / "missing.txt")

    assert result == real / "missing.txt"
    assert not result.exists()


def test_normalize_entry_path_preserves_entry_name_after_parent_resolution(
    tmp_path,
) -> None:
    """Only the parent path is resolved; the entry name is retained."""
    real = tmp_path / "real"
    real.mkdir()

    link = tmp_path / "link"
    _symlink_or_skip(link, real)

    entry_name = "entry.txt"
    result = normalize_entry_path(link / entry_name)

    assert result.name == entry_name
    assert result.parent == real
