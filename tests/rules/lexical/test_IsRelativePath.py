from pathlib import Path
from simplibs.exception import ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import IsRelativePath


def test_is_relative_path_contract(subtests, tmp_path) -> None:
    """Verify the complete contract of the IsRelativePath rule."""
    assert_rule_contract(
        subtests,
        rule=IsRelativePath(),
        valid_values=["rel/x", Path("a"), ".", "..", "a/b/../c"],
        invalid_values=[tmp_path, str(tmp_path), "~", "", "   ", "a\0b", None, 5, b"x"],
        expected_error_name="IS_RELATIVE_PATH_ERROR",
        expected_description="relative path",
        verbose=False,
    )


def test_is_relative_path_is_not_simply_the_negation_of_absolute() -> None:
    """A non-path is neither absolute nor relative."""
    from simplibs.path.rules import IsAbsolutePath
    assert IsAbsolutePath().is_valid(None) is False
    assert IsRelativePath().is_valid(None) is False


def test_is_relative_path_card(subtests, tmp_path) -> None:
    assert_exception_function(
        subtests,
        func=IsRelativePath().validate,
        invalid_params=(tmp_path, Kwargs(value_name="target")),
        exception_type=ValidationError,
        error_name="IS_RELATIVE_PATH_ERROR",
        label="target",
        value=tmp_path,
        expected="a relative path",
        problem=f"Path {tmp_path!r} is absolute.",
        how_to_fix="Provide a relative path, or make it relative with relativize_path().",
        exception=ValueError,
        verbose=False,
    )
