from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import NotFoundError, StateError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import EnsureFile


def test_ensure_file_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the EnsureFile action."""
    assert_action(
        subtests,
        EnsureFile(),
        valid_values=[tmp_path / "new.txt", str(tmp_path / "sub" / "b.txt")],
        expected_outputs=[(tmp_path / "new.txt").resolve(), (tmp_path / "sub" / "b.txt").resolve()],
        invalid_values=[5, "", tmp_path],
        expected_exception_type=[ValidationError, ValidationError, StateError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=EnsureFile,
        invalid_init_params=[((), {"create": "yes"}), ((), {"create": None})],
        verbose=False,
    )


def test_ensure_file_really_creates_an_empty_file(tmp_path) -> None:
    EnsureFile()(tmp_path / "a" / "new.txt")
    assert (tmp_path / "a" / "new.txt").is_file()
    assert (tmp_path / "a" / "new.txt").stat().st_size == 0


def test_ensure_file_without_create_is_a_precondition(tmp_path) -> None:
    existing = tmp_path / "there.txt"
    existing.write_text("x")
    action = EnsureFile(create=False)
    assert action(existing) == existing.resolve()
    with pytest.raises(NotFoundError):
        action(tmp_path / "missing.txt")
    assert not (tmp_path / "missing.txt").exists()
