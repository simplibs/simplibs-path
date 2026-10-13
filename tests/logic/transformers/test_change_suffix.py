from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.path.logic.transformers import change_suffix


@pytest.mark.parametrize(
    "path, new_suffix, expected",
    [
        ("dir/report.txt", ".md", "dir/report.md"),
        ("dir/report", ".md", "dir/report.md"),
        ("dir/report.txt", "", "dir/report"),
        ("archive.tar.gz", ".zip", "archive.tar.zip"),
        (".bashrc", ".bak", ".bashrc.bak"),
        ("dir/report.txt", ".tar.gz", "dir/report.tar.gz"),
        ("dir/report.TXT", ".md", "dir/report.md"),
    ],
)
def test_change_suffix_replaces_adds_or_removes(path, new_suffix, expected) -> None:
    """The last suffix is replaced, added, or (with an empty string) removed."""
    assert change_suffix(path, new_suffix) == Path(expected)


def test_change_suffix_accepts_path_instances() -> None:
    """A Path instance works the same as a string."""
    assert change_suffix(Path("a/b.txt"), ".md") == Path("a/b.md")


def test_change_suffix_does_not_touch_the_disk_or_expand_user() -> None:
    """The change is purely lexical — '~' stays '~'."""
    assert change_suffix("~/notes.txt", ".md") == Path("~/notes.md")


@pytest.mark.parametrize("bad_suffix", ["txt", ".", "/etc", ".a/b", ".a\\b", ".a\0b"])
def test_change_suffix_rejects_malformed_suffix(bad_suffix) -> None:
    """A suffix without a leading dot, a lone dot, or one with separators is rejected."""
    with pytest.raises(ParamError):
        change_suffix("dir/report.txt", bad_suffix)


@pytest.mark.parametrize("nameless", [".", ".."])
def test_change_suffix_rejects_nameless_paths(nameless) -> None:
    """'.' and '..' have no final name that could carry a suffix."""
    with pytest.raises(ParamError):
        change_suffix(nameless, ".txt")


def test_change_suffix_rejects_a_filesystem_root() -> None:
    """A filesystem root has no final name either."""
    with pytest.raises(ParamError):
        change_suffix(Path.cwd().anchor, ".txt")


@pytest.mark.parametrize("value", ["", "  ", None, 5])
def test_change_suffix_rejects_invalid_path_input(value) -> None:
    """Blank strings and non-path types are rejected by the PathLike annotation."""
    with pytest.raises(ValidationError):
        change_suffix(value, ".txt")


def test_change_suffix_rejects_non_string_suffix() -> None:
    """The suffix itself must be a string."""
    with pytest.raises(ValidationError):
        change_suffix("a.txt", 5)
