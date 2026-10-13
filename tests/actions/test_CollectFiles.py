import inspect
from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import NotFoundError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import CollectFiles


def test_collect_files_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the CollectFiles action."""
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "b.txt").write_text("x")
    base = tmp_path.resolve()
    assert_action(
        subtests,
        CollectFiles(),
        valid_values=[tmp_path, str(tmp_path)],
        expected_outputs=[[base / "a.py", base / "sub" / "b.txt"]] * 2,
        invalid_values=[5, "", tmp_path / "missing"],
        expected_exception_type=[ValidationError, ValidationError, NotFoundError],
        expected_input_type=PathLike,
        expected_output_type=list[Path],
        action_class=CollectFiles,
        invalid_init_params=[((), {"recursive": "x"}), ((), {"exclude_filter": 5})],
        verbose=False,
    )


def test_collect_files_cannot_be_told_to_collect_directories() -> None:
    """The type flags are not part of the action's constructor — the lock is real."""
    parameters = inspect.signature(CollectFiles.__init__).parameters
    assert "collect_dirs" not in parameters and "collect_files" not in parameters
    with pytest.raises(TypeError):
        CollectFiles(collect_dirs=True)


def test_collect_files_never_returns_directories(tmp_path) -> None:
    (tmp_path / "dir").mkdir()
    (tmp_path / "f.txt").write_text("x")
    assert [p.name for p in CollectFiles()(tmp_path)] == ["f.txt"]
