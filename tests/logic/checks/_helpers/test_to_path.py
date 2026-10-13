from pathlib import Path
import pytest
from simplibs.path.logic.checks._helpers import to_path


@pytest.mark.parametrize(
    "value, expected",
    [
        ("dir/file.txt", Path("dir/file.txt")),
        (Path("dir/file.txt"), Path("dir/file.txt")),
        (".", Path(".")),
        ("~", Path.home()),
    ],
)
def test_to_path_converts_valid_candidates(value, expected) -> None:
    """A str or Path becomes a Path, with a leading '~' expanded."""
    assert to_path(value) == expected


@pytest.mark.parametrize(
    "value",
    [None, 42, 1.5, b"file.txt", ["a"], "", "   ", "\t\n", "a\0b", Path("a\0b")],
)
def test_to_path_returns_none_for_non_paths(value) -> None:
    """Non-str/Path values, blank strings and null bytes are not paths."""
    assert to_path(value) is None


def test_to_path_never_raises_for_unknown_user() -> None:
    """'~unknown_user' is None on POSIX and a sibling path on Windows — but never raises."""
    result = to_path("~no_such_user_for_sure_123")
    assert result is None or isinstance(result, Path)


def test_to_path_does_not_resolve_or_touch_the_disk() -> None:
    """A path that cannot exist is returned as given — no resolve(), no stat()."""
    value = "definitely/not/existing/../here"
    assert to_path(value) == Path(value)
