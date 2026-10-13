import inspect
from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import NotFoundError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import CollectDirs


def test_collect_dirs_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the CollectDirs action."""
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "deep").mkdir()
    base = tmp_path.resolve()
    assert_action(
        subtests,
        CollectDirs(),
        valid_values=[tmp_path, str(tmp_path)],
        expected_outputs=[[base / "sub", base / "sub" / "deep"]] * 2,
        invalid_values=[5, "", tmp_path / "missing"],
        expected_exception_type=[ValidationError, ValidationError, NotFoundError],
        expected_input_type=PathLike,
        expected_output_type=list[Path],
        action_class=CollectDirs,
        invalid_init_params=[((), {"recursive": "x"}), ((), {"include_filter": 5})],
        verbose=False,
    )


def test_collect_dirs_cannot_be_told_to_collect_files() -> None:
    parameters = inspect.signature(CollectDirs.__init__).parameters
    assert "collect_dirs" not in parameters and "collect_files" not in parameters
    with pytest.raises(TypeError):
        CollectDirs(collect_files=True)


def test_collect_dirs_excludes_the_root_itself(tmp_path) -> None:
    (tmp_path / "sub").mkdir()
    assert tmp_path.resolve() not in CollectDirs()(tmp_path)
