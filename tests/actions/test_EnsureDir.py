import asyncio
from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import StateError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import EnsureDir


def test_ensure_dir_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the EnsureDir action."""
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    assert_action(
        subtests,
        EnsureDir(),
        valid_values=[tmp_path / "new", str(tmp_path / "a" / "b"), tmp_path],
        expected_outputs=[(tmp_path / "new").resolve(), (tmp_path / "a" / "b").resolve(), tmp_path.resolve()],
        invalid_values=[5, "", blocker],
        expected_exception_type=[ValidationError, ValidationError, StateError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=EnsureDir,
        verbose=False,
    )


def test_ensure_dir_really_creates_the_directory(tmp_path) -> None:
    EnsureDir()(tmp_path / "x" / "y")
    assert (tmp_path / "x" / "y").is_dir()


def test_ensure_dir_runs_asynchronously(tmp_path) -> None:
    result = asyncio.run(EnsureDir().acall(tmp_path / "async_dir"))
    assert result == (tmp_path / "async_dir").resolve()
    assert (tmp_path / "async_dir").is_dir()
