from pathlib import Path
from simplibs.actions.testing import assert_action
from simplibs.exception import StateError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import EnsureParentDir


def test_ensure_parent_dir_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the EnsureParentDir action."""
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    assert_action(
        subtests,
        EnsureParentDir(),
        valid_values=[tmp_path / "out" / "a.md", str(tmp_path / "deep" / "er" / "b.md")],
        expected_outputs=[(tmp_path / "out" / "a.md").resolve(), (tmp_path / "deep" / "er" / "b.md").resolve()],
        invalid_values=[5, "", blocker / "x.md"],
        expected_exception_type=[ValidationError, ValidationError, StateError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=EnsureParentDir,
        verbose=False,
    )


def test_ensure_parent_dir_creates_the_folder_but_not_the_file(tmp_path) -> None:
    target = tmp_path / "out" / "a.md"
    result = EnsureParentDir()(target)
    assert (tmp_path / "out").is_dir()
    assert not target.exists()
    assert result == target.resolve()
