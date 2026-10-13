from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import RelativizePath


def test_relativize_path_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the RelativizePath action."""
    assert_action(
        subtests,
        RelativizePath(root=tmp_path),
        valid_values=[tmp_path / "src" / "a.py", str(tmp_path / "b.txt"), tmp_path],
        expected_outputs=[Path("src/a.py"), Path("b.txt"), Path(".")],
        invalid_values=[5, "", tmp_path.parent / "other" / "x.py"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=RelativizePath,
        invalid_init_params=[((), {"root": ""}), ((), {"root": None}), ((), {"root": 5})],
        verbose=False,
    )


def test_relativize_path_requires_a_root() -> None:
    with pytest.raises(TypeError):
        RelativizePath()
