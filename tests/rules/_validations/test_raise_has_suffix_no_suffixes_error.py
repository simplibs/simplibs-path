from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.rules._validations import raise_has_suffix_no_suffixes_error


def test_raise_has_suffix_no_suffixes_error_contract(subtests) -> None:
    def raising_wrapper():
        raise_has_suffix_no_suffixes_error()

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(),
        exception_type=ParamError,
        error_name="HAS_SUFFIX_NO_SUFFIXES_ERROR",
        label="HasSuffix.suffixes",
        expected="At least one suffix, e.g. HasSuffix('.py') or HasSuffix('.md', '.rst').",
        value=(),
        problem=(
            "HasSuffix() was created without any suffix.",
            "A rule without a suffix to look for could never accept or reject anything.",
        ),
        how_to_fix=("Pass one or more suffixes: HasSuffix('.py').",),
        verbose=False,
    )
