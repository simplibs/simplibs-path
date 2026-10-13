import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.rules._validations import raise_rule_param_not_bool_error


@pytest.mark.parametrize(
    "rule_name, param_name, value",
    [("HasSuffix", "ignore_case", "yes"), ("IsWithin", "allow_equal", 1), ("IsHidden", "check_attributes", None)],
)
def test_raise_rule_param_not_bool_error_contract(subtests, rule_name, param_name, value) -> None:
    def raising_wrapper(rule, param, val):
        raise_rule_param_not_bool_error(rule, param, val)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(rule_name, param_name, value),
        exception_type=ParamError,
        error_name="RULE_PARAM_NOT_BOOL_ERROR",
        label=f"{rule_name}.{param_name}",
        expected="True or False.",
        value=value,
        problem=(
            f"Parameter '{param_name}' of {rule_name}() must be a bool, "
            f"got {value!r} of type '{type(value).__name__}'.",
        ),
        how_to_fix=(f"Pass True or False as '{param_name}'.",),
        verbose=False,
    )
