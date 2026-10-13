from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import IsValidFilename


def test_is_valid_filename_contract(subtests) -> None:
    """Verify the complete contract of the IsValidFilename rule."""
    assert_rule_contract(
        subtests,
        rule=IsValidFilename(),
        valid_values=["report.txt", ".bashrc", "archive.tar.gz", Path("dir/report.md"), "ěščř.md"],
        invalid_values=["a/b", "", "   ", "con", "a:b", "a?b", "name.", "a" * 256, ".", "..", Path("dir/con.txt"), None, 5, b"x"],
        expected_error_name="IS_VALID_FILENAME_ERROR",
        expected_description="portable file name",
        rule_factory=IsValidFilename,
        invalid_init_params=[
            ((), {"portable": "yes"}),
            ((), {"portable": 0}),
            ((), {"portable": None}),
        ],
        verbose=False,
    )


def test_is_valid_filename_non_portable_description() -> None:
    assert IsValidFilename(portable=False).describe() == "file name valid on this OS"


def test_is_valid_filename_portable_must_be_keyword_only() -> None:
    with pytest.raises(TypeError):
        IsValidFilename(False)


def test_is_valid_filename_a_str_is_a_name_a_path_is_judged_by_its_final_name() -> None:
    rule = IsValidFilename()
    assert rule.is_valid("dir/report.md") is False
    assert rule.is_valid(Path("dir/report.md")) is True


def test_is_valid_filename_non_portable_still_rejects_universal_problems() -> None:
    rule = IsValidFilename(portable=False)
    assert rule.is_valid("a/b") is False
    assert rule.is_valid("report.txt") is True


def test_is_valid_filename_card_names_the_concrete_reason(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsValidFilename().validate,
        invalid_params=("what?.txt", Kwargs(value_name="title", context="step")),
        exception_type=ValidationError,
        error_name="IS_VALID_FILENAME_ERROR",
        label="title",
        context="step",
        value="what?.txt",
        expected="a portable file name",
        problem="'what?.txt' is not a usable file name (contains the character '?', which Windows forbids in names).",
        how_to_fix="Provide a name without separators, forbidden characters or reserved names.",
        exception=ValueError,
        verbose=False,
    )


def test_is_valid_filename_card_for_a_path_reports_its_final_name(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsValidFilename().validate,
        invalid_params=(Path("dir/con.txt"),),
        exception_type=ValidationError,
        error_name="IS_VALID_FILENAME_ERROR",
        problem="'con.txt' is not a usable file name ('CON' is a reserved Windows device name).",
        exception=ValueError,
        verbose=False,
    )


def test_is_valid_filename_card_for_a_non_path(subtests) -> None:
    assert_exception_function(
        subtests,
        func=IsValidFilename().validate,
        invalid_params=(5, Kwargs(value_name="title")),
        exception_type=ValidationError,
        error_name="IS_VALID_FILENAME_ERROR",
        label="title",
        value=5,
        problem="Value 5 of type 'int' is not a string or Path.",
        exception=TypeError,
        verbose=False,
    )


def test_is_valid_filename_unreachable_fallback_for_a_fine_name() -> None:
    exc = IsValidFilename().build_exception("report.txt", value_name="title")
    assert isinstance(exc, ValidationError)
    assert exc.error_name == "IS_VALID_FILENAME_UNREACHABLE_ERROR"
    assert exc.exception is RuntimeError
