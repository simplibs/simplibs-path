"""Tests: the public path tools facade re-exports the original helpers."""

from simplibs.path import tools
from simplibs.path.logic.checks._helpers import to_path
from simplibs.path.logic.transformers._helpers import is_valid_suffix
from simplibs.path.rules._helpers import (
    build_not_a_path_exception,
    build_path_rule_exception,
    check_path,
)


def test_tools_exports_expected_names():
    """Verify __all__ contains exactly the intended public names."""
    assert tools.__all__ == [
        "to_path",
        "is_valid_suffix",
        "check_path",
        "build_path_rule_exception",
        "build_not_a_path_exception",
    ]

    assert all(hasattr(tools, name) for name in tools.__all__)


def test_tools_re_exports_original_objects():
    """Verify every public export is the original object."""
    assert tools.to_path is to_path
    assert tools.is_valid_suffix is is_valid_suffix
    assert tools.check_path is check_path
    assert tools.build_path_rule_exception is build_path_rule_exception
    assert tools.build_not_a_path_exception is build_not_a_path_exception