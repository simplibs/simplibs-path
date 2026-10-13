import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.rules._validations import raise_has_suffix_invalid_suffix_error


@pytest.mark.parametrize("suffix", ["py", ".", "/x", 5, None])
def test_raise_has_suffix_invalid_suffix_error_contract(subtests, suffix) -> None:
    def raising_wrapper(value):
        raise_has_suffix_invalid_suffix_error(value)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(suffix,),
        exception_type=ParamError,
        error_name="HAS_SUFFIX_INVALID_SUFFIX_ERROR",
        label="HasSuffix.suffixes",
        expected="Strings such as '.py', '.tar.gz', or '' for a name without a suffix.",
        value=suffix,
        problem=(
            f"{suffix!r} is not a valid file suffix.",
            "A suffix must be an empty string (no suffix) or a string such as '.txt', "
            "without any path separator.",
        ),
        how_to_fix=(
            "Start each suffix with a dot, e.g. '.py' instead of 'py'.",
            "Remove path separators from the suffix.",
        ),
        verbose=False,
    )
