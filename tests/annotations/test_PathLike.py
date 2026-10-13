from pathlib import Path
import pytest
from simplibs.rules import IsTyping
from simplibs.path.annotations import PathLike


@pytest.mark.parametrize(
    "value",
    ["file.txt", "dir/sub", ".", "~", Path("dir/file.txt"), Path(".")],
)
def test_path_like_accepts_paths(value) -> None:
    """A non-blank string or any Path instance is a valid path input."""
    assert IsTyping(PathLike).is_valid(value)


@pytest.mark.parametrize(
    "value",
    ["", "   ", "\t", None, 42, 1.5, b"file.txt", ["a"], {"a": 1}],
)
def test_path_like_rejects_everything_else(value) -> None:
    """Blank strings and non-path types are rejected."""
    assert not IsTyping(PathLike).is_valid(value)
