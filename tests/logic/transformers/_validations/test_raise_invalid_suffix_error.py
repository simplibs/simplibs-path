import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.logic.transformers._validations import raise_invalid_suffix_error


@pytest.mark.parametrize("suffix", ["txt", ".", "/etc", ".a/b"])
def test_raise_invalid_suffix_error_contract(subtests, suffix) -> None:
    """Verify raise_invalid_suffix_error produces a well-formed ParamError card."""

    def raising_wrapper(target_suffix):
        raise_invalid_suffix_error(target_suffix)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(suffix,),
        exception_type=ParamError,
        error_name="INVALID_PATH_SUFFIX",
        label="new_suffix",
        expected="An empty string (removes the suffix) or a string such as '.txt'.",
        value=suffix,
        problem=(
            f"Suffix {suffix!r} is not a valid file suffix.",
            "A suffix must be empty, or start with a dot followed by at least one character, "
            "without any path separator.",
        ),
        how_to_fix=(
            "Start the suffix with a dot, e.g. '.txt' instead of 'txt'.",
            "Remove path separators ('/' or '\\\\') from the suffix.",
            "Use an empty string if the suffix should be removed.",
        ),
        verbose=False,
    )
