from pathlib import Path
from simplibs.exception import ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import IsAbsolutePath


def test_is_absolute_path_contract(subtests, tmp_path) -> None:
    """Verify the complete contract of the IsAbsolutePath rule."""
    assert_rule_contract(
        subtests,
        rule=IsAbsolutePath(),
        valid_values=[tmp_path, str(tmp_path), tmp_path / "missing" / "x.txt", "~"],
        invalid_values=["rel/x", Path("a"), ".", "..", "", "   ", "a\0b", None, 5, b"x"],
        expected_error_name="IS_ABSOLUTE_PATH_ERROR",
        expected_description="absolute path",
        verbose=False,
    )


def test_is_absolute_path_does_not_touch_the_disk(tmp_path) -> None:
    assert IsAbsolutePath().is_valid(tmp_path / "does" / "not" / "exist") is True


def test_is_absolute_path_card(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsAbsolutePath().validate,
        invalid_params=("rel/x", Kwargs(value_name="target", context="step")),
        exception_type=ValidationError,
        error_name="IS_ABSOLUTE_PATH_ERROR",
        label="target",
        context="step",
        value="rel/x",
        expected="an absolute path",
        problem="Path 'rel/x' is not absolute.",
        how_to_fix="Provide an absolute path, or make it absolute with normalize_path().",
        exception=ValueError,
        verbose=False,
    )


def test_is_absolute_path_card_for_a_non_path(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsAbsolutePath().validate,
        invalid_params=(5,),
        exception_type=ValidationError,
        error_name="IS_ABSOLUTE_PATH_ERROR",
        value=5,
        problem="Value 5 of type 'int' is not a string or Path.",
        exception=TypeError,
        verbose=False,
    )
