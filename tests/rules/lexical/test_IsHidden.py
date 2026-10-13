import os
from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import IsHidden


def test_is_hidden_contract(subtests) -> None:
    """Verify the complete contract of the IsHidden rule."""
    assert_rule_contract(
        subtests,
        rule=IsHidden(),
        valid_values=[".git", "dir/.env", Path(".x"), "/abs/dir/.config"],
        invalid_values=["file.txt", "dir/file", ".", "..", "/abs/.hidden_dir/file.txt", "", "a\0.b", None, 5],
        expected_error_name="IS_HIDDEN_ERROR",
        expected_description="hidden path",
        rule_factory=IsHidden,
        invalid_init_params=[
            ((), {"check_attributes": "yes"}),
            ((), {"check_attributes": 1}),
            ((), {"check_attributes": None}),
        ],
        verbose=False,
    )


def test_is_hidden_check_attributes_must_be_keyword_only() -> None:
    with pytest.raises(TypeError):
        IsHidden(True)


def test_is_hidden_stores_its_option() -> None:
    assert IsHidden().check_attributes is False
    assert IsHidden(check_attributes=True).check_attributes is True


def test_is_hidden_check_attributes_has_no_effect_on_ordinary_files(tmp_path) -> None:
    target = tmp_path / "plain.txt"
    target.write_text("x")
    assert IsHidden(check_attributes=True).is_valid(target) is False


@pytest.mark.skipif(os.name != "nt", reason="The hidden attribute exists on Windows only")
def test_is_hidden_detects_the_windows_attribute(tmp_path) -> None:
    import ctypes
    target = tmp_path / "visible_name.txt"
    target.write_text("x")
    assert ctypes.windll.kernel32.SetFileAttributesW(str(target), 0x2)
    assert IsHidden().is_valid(target) is False
    assert IsHidden(check_attributes=True).is_valid(target) is True


def test_is_hidden_card(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsHidden().validate,
        invalid_params=("file.txt", Kwargs(value_name="entry", context="step")),
        exception_type=ValidationError,
        error_name="IS_HIDDEN_ERROR",
        label="entry",
        context="step",
        value="file.txt",
        expected="a hidden path (its name starts with a dot)",
        problem="Path 'file.txt' is not hidden.",
        how_to_fix="Provide a path whose final name starts with a dot, such as '.git'.",
        exception=ValueError,
        verbose=False,
    )


def test_is_hidden_composes_as_a_filter(tmp_path) -> None:
    from simplibs.path.logic.scanners import collect_paths
    (tmp_path / "keep.txt").write_text("x")
    (tmp_path / ".secret").write_text("x")
    names = [p.name for p in collect_paths(tmp_path, exclude_filter=IsHidden(), ignore_names=None)]
    assert names == ["keep.txt"]
