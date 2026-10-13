import asyncio
import os
from pathlib import Path

import pytest

from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import AccessError, ParamError, ValidationError
from simplibs.path.actions import NormalizeEntryPath
from simplibs.path.annotations import PathLike


def test_normalize_entry_path_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the action."""
    messy = tmp_path / "a" / ".." / "b.txt"
    expected = (tmp_path / "b.txt").resolve()

    assert_action(
        subtests,
        NormalizeEntryPath(),
        valid_values=[messy, str(messy)],
        expected_outputs=[expected, expected],
        invalid_values=[5, "", None, "bad\0path"],
        expected_exception_type=[
            ValidationError,
            ValidationError,
            ValidationError,
            AccessError,
        ],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=NormalizeEntryPath,
        verbose=False,
    )


def test_normalize_entry_path_is_an_action_with_the_function_docstring() -> None:
    assert issubclass(NormalizeEntryPath, Action)
    assert NormalizeEntryPath.__name__ == "NormalizeEntryPath"
    assert "Normalize the path of a directory ENTRY" in NormalizeEntryPath.__doc__


def test_normalize_entry_path_rejects_a_filesystem_root() -> None:
    """A root has no final entry name."""
    with pytest.raises(ParamError):
        NormalizeEntryPath()(Path.cwd().anchor)


def test_normalize_entry_path_resolves_a_symlinked_parent(tmp_path) -> None:
    """A symlink in the directory part is resolved."""
    real = tmp_path / "real"
    real.mkdir()

    link = tmp_path / "link"

    try:
        link.symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")

    result = NormalizeEntryPath()(link / "file.txt")

    assert result == (real / "file.txt").resolve()


def test_normalize_entry_path_preserves_a_final_symlink(tmp_path) -> None:
    """The final symlink name is preserved instead of following its target."""
    link = tmp_path / "link.txt"

    try:
        link.symlink_to(tmp_path / "nowhere.txt")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")

    result = NormalizeEntryPath()(link)

    assert result == link
    assert result.name == "link.txt"


def test_normalize_entry_path_runs_asynchronously_in_a_thread(tmp_path) -> None:
    messy = tmp_path / "a" / ".." / "b.txt"

    assert asyncio.run(
        NormalizeEntryPath().acall(messy)
    ) == (tmp_path / "b.txt").resolve()
