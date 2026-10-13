from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ValidationError
from simplibs.path.actions import FilterPaths
from simplibs.path.rules import HasSuffix


PATHS = [Path("a.py"), Path("b.md"), Path("dir/c.py")]


def test_filter_paths_contract(subtests) -> None:
    """Verify the execution and construction contract of the FilterPaths action."""
    assert_action(
        subtests,
        FilterPaths(rule=HasSuffix(".py")),
        valid_values=[PATHS, tuple(PATHS), set()],
        expected_outputs=[[Path("a.py"), Path("dir/c.py")], [Path("a.py"), Path("dir/c.py")], []],
        invalid_values=[5, "a.py", (path for path in PATHS), [Path("a.py"), "b.md"]],
        expected_exception_type=ValidationError,
        expected_output_type=list[Path],
        action_class=FilterPaths,
        invalid_init_params=[((), {"rule": 5}), ((), {"rule": None}), ((), {"rule": "suffix"})],
        verbose=False,
    )


def test_filter_paths_requires_a_rule() -> None:
    with pytest.raises(TypeError):
        FilterPaths()


def test_filter_paths_accepts_a_plain_function() -> None:
    assert FilterPaths(rule=lambda p: p.suffix == ".md")(PATHS) == [Path("b.md")]


def test_filter_paths_preserves_order() -> None:
    assert FilterPaths(rule=lambda p: True)(PATHS) == PATHS
