from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import OperationError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import MakeUniquePath


def test_make_unique_path_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the MakeUniquePath action."""
    (tmp_path / "taken.txt").write_text("x")
    assert_action(
        subtests,
        MakeUniquePath(),
        valid_values=[tmp_path / "free.txt", tmp_path / "taken.txt"],
        expected_outputs=[(tmp_path / "free.txt").resolve(), (tmp_path / "taken (1).txt").resolve()],
        invalid_values=[5, ""],
        expected_exception_type=ValidationError,
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=MakeUniquePath,
        invalid_init_params=[((), {"max_attempts": 0}), ((), {"max_attempts": -1}), ((), {"max_attempts": "3"})],
        verbose=False,
    )


def test_make_unique_path_gives_up_after_max_attempts(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("x")
    (tmp_path / "a (1).txt").write_text("x")
    with pytest.raises(OperationError):
        MakeUniquePath(max_attempts=1)(tmp_path / "a.txt")


def test_make_unique_path_creates_nothing(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("x")
    MakeUniquePath()(tmp_path / "a.txt")
    assert sorted(p.name for p in tmp_path.iterdir()) == ["a.txt"]
