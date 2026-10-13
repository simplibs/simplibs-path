from simplibs.exception import ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import IsDir


def test_is_dir_contract(subtests, tmp_path) -> None:
    """Verify the complete contract of the IsDir rule."""
    file = tmp_path / "a.txt"
    file.write_text("x")
    missing = tmp_path / "missing"
    assert_rule_contract(
        subtests,
        rule=IsDir(),
        valid_values=[tmp_path, str(tmp_path)],
        invalid_values=[file, str(file), missing, "", "   ", "a\0b", None, 5, b"x", []],
        expected_error_name="IS_DIR_ERROR",
        expected_description="existing directory",
        verbose=False,
    )


def test_is_dir_card_for_a_usable_path_that_fails(subtests, tmp_path) -> None:
    file = tmp_path / "a.txt"
    file.write_text("x")
    missing = tmp_path / "missing"
    bad = file
    assert_exception_function(
        subtests,
        func=IsDir().validate,
        invalid_params=(bad, Kwargs(value_name="source", context="step")),
        exception_type=ValidationError,
        error_name="IS_DIR_ERROR",
        label="source",
        context="step",
        value=bad,
        expected="an existing directory",
        problem=f"Path {bad!r} is not an existing directory.",
        how_to_fix="Provide a path to an existing directory.",
        exception=ValueError,
        verbose=False,
    )


def test_is_dir_card_for_a_non_path(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsDir().validate,
        invalid_params=(5, Kwargs(value_name="source")),
        exception_type=ValidationError,
        error_name="IS_DIR_ERROR",
        label="source",
        value=5,
        expected="an existing directory",
        problem="Value 5 of type 'int' is not a string or Path.",
        how_to_fix="Provide a path as a str or a Path object.",
        exception=TypeError,
        verbose=False,
    )


def test_is_dir_card_for_a_blank_string(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsDir().validate,
        invalid_params=("",),
        exception_type=ValidationError,
        error_name="IS_DIR_ERROR",
        value="",
        problem="Value '' cannot be used as a path (it is blank or contains a null byte).",
        how_to_fix="Provide a non-blank path without null bytes.",
        exception=ValueError,
        verbose=False,
    )
