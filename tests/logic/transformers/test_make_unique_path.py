from pathlib import Path

import pytest

from simplibs.exception import OperationError, ParamError, ValidationError
from simplibs.path.logic.transformers import make_unique_path


def test_make_unique_path_keeps_a_free_path(tmp_path) -> None:
    """A path that does not exist is returned as it is (normalized)."""
    target = tmp_path / "report.txt"

    assert make_unique_path(target) == target.resolve()


def test_make_unique_path_numbers_an_existing_file(tmp_path) -> None:
    """An existing file gets ' (1)' before its extension."""
    (tmp_path / "report.txt").write_text("x")

    assert make_unique_path(tmp_path / "report.txt") == (
        tmp_path / "report (1).txt"
    ).resolve()


def test_make_unique_path_skips_taken_numbers(tmp_path) -> None:
    """The first free number is used."""
    (tmp_path / "report.txt").write_text("x")
    (tmp_path / "report (1).txt").write_text("x")
    (tmp_path / "report (2).txt").write_text("x")

    assert make_unique_path(tmp_path / "report.txt") == (
        tmp_path / "report (3).txt"
    ).resolve()


def test_make_unique_path_fills_the_first_gap(tmp_path) -> None:
    """A gap in the numbering is reused."""
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "a (2).txt").write_text("x")

    assert make_unique_path(tmp_path / "a.txt") == (
        tmp_path / "a (1).txt"
    ).resolve()


def test_make_unique_path_numbers_a_directory(tmp_path) -> None:
    """A directory name is numbered the same way."""
    (tmp_path / "out").mkdir()

    assert make_unique_path(tmp_path / "out") == (
        tmp_path / "out (1)"
    ).resolve()


def test_make_unique_path_keeps_tar_gz_together(tmp_path) -> None:
    """`.tar.gz` stays one suffix."""
    (tmp_path / "archive.tar.gz").write_text("x")

    assert make_unique_path(tmp_path / "archive.tar.gz") == (
        tmp_path / "archive (1).tar.gz"
    ).resolve()


def test_make_unique_path_handles_hidden_files(tmp_path) -> None:
    """A dotfile has no suffix; the number goes at the end."""
    (tmp_path / ".env").write_text("x")

    assert make_unique_path(tmp_path / ".env") == (
        tmp_path / ".env (1)"
    ).resolve()


def test_make_unique_path_creates_nothing(tmp_path) -> None:
    """Only a name is chosen; nothing is written."""
    (tmp_path / "a.txt").write_text("x")

    make_unique_path(tmp_path / "a.txt")

    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.txt"]


def test_make_unique_path_treats_a_broken_symlink_as_taken(tmp_path) -> None:
    """A dangling symlink occupies its name."""
    link = tmp_path / "dangling.txt"

    try:
        link.symlink_to(tmp_path / "nowhere")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")

    assert make_unique_path(link) == (
        tmp_path / "dangling (1).txt"
    ).resolve()


def test_make_unique_path_gives_up_after_max_attempts(tmp_path) -> None:
    """An OperationError is raised when every numbered variant is taken."""
    (tmp_path / "a.txt").write_text("x")

    for number in (1, 2, 3):
        (tmp_path / f"a ({number}).txt").write_text("x")

    with pytest.raises(OperationError):
        make_unique_path(tmp_path / "a.txt", max_attempts=3)


def test_make_unique_path_succeeds_on_the_last_allowed_attempt(tmp_path) -> None:
    """The limit counts attempts inclusively."""
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "a (1).txt").write_text("x")

    assert make_unique_path(
        tmp_path / "a.txt",
        max_attempts=2,
    ) == (tmp_path / "a (2).txt").resolve()


def test_make_unique_path_rejects_a_filesystem_root() -> None:
    """A root has no name that could be numbered."""
    with pytest.raises(ParamError):
        make_unique_path(Path.cwd().anchor)


@pytest.mark.parametrize("bad_attempts", [0, -1, 1.5, "3", None])
def test_make_unique_path_rejects_invalid_max_attempts(
    tmp_path,
    bad_attempts,
) -> None:
    """max_attempts must be a positive integer."""
    with pytest.raises(ValidationError):
        make_unique_path(
            tmp_path / "a.txt",
            max_attempts=bad_attempts,
        )


@pytest.mark.parametrize("value", ["", "  ", None, 7])
def test_make_unique_path_rejects_invalid_path_input(value) -> None:
    """Blank strings and non-path types are rejected."""
    with pytest.raises(ValidationError):
        make_unique_path(value)
