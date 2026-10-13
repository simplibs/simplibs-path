import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.rules._validations import raise_rule_param_not_path_error


@pytest.mark.parametrize("value", [5, None, "", "   ", "a\0b"])
def test_raise_rule_param_not_path_error_contract(subtests, value) -> None:
    def raising_wrapper(rule, param, val):
        raise_rule_param_not_path_error(rule, param, val)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=("IsWithin", "root", value),
        exception_type=ParamError,
        error_name="RULE_PARAM_NOT_PATH_ERROR",
        label="IsWithin.root",
        expected="A non-blank string or a Path instance.",
        value=value,
        problem=(
            f"Parameter 'root' of IsWithin() must be a non-blank str or a Path "
            f"without a null byte, got {value!r} of type '{type(value).__name__}'.",
        ),
        how_to_fix=("Pass a directory path as 'root', e.g. Path('src') or 'src'.",),
        verbose=False,
    )
