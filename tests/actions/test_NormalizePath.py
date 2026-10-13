import asyncio
import os
from pathlib import Path
import pytest
from simplibs.actions import Action
from simplibs.actions.testing import assert_action
from simplibs.exception import AccessError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import NormalizePath


def test_normalize_path_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the NormalizePath action."""
    messy = tmp_path / "a" / ".." / "b"
    assert_action(
        subtests,
        NormalizePath(),
        valid_values=[messy, str(messy)],
        expected_outputs=[(tmp_path / "b").resolve(), (tmp_path / "b").resolve()],
        invalid_values=[5, "", None, "bad\0path"],
        expected_exception_type=[ValidationError, ValidationError, ValidationError, AccessError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=NormalizePath,
        invalid_init_params=[((), {"resolve_symlinks": "yes"}), ((), {"resolve_symlinks": None})],
        verbose=False,
    )


def test_normalize_path_is_an_action_with_the_function_docstring() -> None:
    assert issubclass(NormalizePath, Action)
    assert NormalizePath.__name__ == "NormalizePath"
    assert "Normalize a path" in NormalizePath.__doc__


def test_normalize_path_keeps_symlinks_when_asked(tmp_path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    try:
        (tmp_path / "link").symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    kept = NormalizePath(resolve_symlinks=False)(tmp_path / "link" / "f.txt")
    followed = NormalizePath()(tmp_path / "link" / "f.txt")
    assert kept == Path(os.path.abspath(tmp_path / "link" / "f.txt"))
    assert followed == (real / "f.txt").resolve()


def test_normalize_path_runs_asynchronously_in_a_thread(tmp_path) -> None:
    messy = tmp_path / "a" / ".." / "b"
    assert asyncio.run(NormalizePath().acall(messy)) == (tmp_path / "b").resolve()
