from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import ChangeSuffix


def test_change_suffix_contract(subtests) -> None:
    """Verify the execution and construction contract of the ChangeSuffix action."""
    assert_action(
        subtests,
        ChangeSuffix(new_suffix=".md"),
        valid_values=["dir/report.txt", Path("a/b"), "archive.tar.gz"],
        expected_outputs=[Path("dir/report.md"), Path("a/b.md"), Path("archive.tar.md")],
        invalid_values=[5, "", ".", ".."],
        expected_exception_type=[ValidationError, ValidationError, ParamError, ParamError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=ChangeSuffix,
        invalid_init_params=[((), {"new_suffix": 5}), ((), {"new_suffix": None})],
        verbose=False,
    )


def test_change_suffix_can_remove_a_suffix() -> None:
    assert ChangeSuffix(new_suffix="")("dir/report.txt") == Path("dir/report")


@pytest.mark.parametrize("bad", ["md", ".", "/x"])
def test_change_suffix_rejects_a_malformed_suffix_when_it_runs(bad) -> None:
    with pytest.raises(ParamError):
        ChangeSuffix(new_suffix=bad)("a.txt")


def test_change_suffix_requires_a_suffix() -> None:
    with pytest.raises(TypeError):
        ChangeSuffix()
