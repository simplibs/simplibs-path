"""Tests: the public path tools facade re-exports the original helpers."""

import importlib
import pytest

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


_NAMES = ["to_path", "is_valid_suffix", "check_path", "build_path_rule_exception", "build_not_a_path_exception"]


def test_tools_exports_exactly_the_documented_names() -> None:
    """`__all__` is the contract of the package — nothing missing, nothing extra."""
    assert sorted(tools.__all__) == sorted(_NAMES)


@pytest.mark.parametrize("name", _NAMES)
def test_every_exported_name_is_importable_and_callable(name: str) -> None:
    """`from simplibs.path.tools import <name>` works and gives a function."""
    assert callable(getattr(tools, name))


@pytest.mark.parametrize(
    "name, module",
    [
        ("to_path", "simplibs.path.logic.checks._helpers"),
        ("is_valid_suffix", "simplibs.path.logic.transformers._helpers"),
        ("check_path", "simplibs.path.rules._helpers"),
        ("build_path_rule_exception", "simplibs.path.rules._helpers"),
        ("build_not_a_path_exception", "simplibs.path.rules._helpers"),
    ],
)
def test_tools_is_a_facade_it_re_exports_the_original_objects(name: str, module: str) -> None:
    """Nothing is copied: the toolkit and the internal location hold the very same function."""
    assert getattr(tools, name) is getattr(importlib.import_module(module), name)


def test_the_package_root_does_not_export_the_tools() -> None:
    """They are for authors of rules, not for the users of the path functions."""
    import simplibs.path as root

    assert not any(hasattr(root, name) for name in _NAMES)