import pytest
from simplibs.exception.testing import assert_exception_function
from simplibs.exception import ParamError
from simplibs.path.rules._validations import raise_rule_param_not_callable_error


@pytest.mark.parametrize("rule_name, value", [("NameIs", "text"), ("StemIs", None), ("ParentNameIs", 5)])
def test_raise_rule_param_not_callable_error_contract(subtests, rule_name, value) -> None:
    def raising_wrapper(rule, param, val):
        raise_rule_param_not_callable_error(rule, param, val)

    assert_exception_function(
        subtests,
        raising_wrapper,
        invalid_params=(rule_name, "rule", value),
        exception_type=ParamError,
        error_name="RULE_PARAM_NOT_CALLABLE_ERROR",
        label=f"{rule_name}.rule",
        expected="A Rule instance or a callable taking one value and returning a bool.",
        value=value,
        problem=(
            f"Parameter 'rule' of {rule_name}() must be a Rule or a callable, "
            f"got {value!r} of type '{type(value).__name__}'.",
        ),
        how_to_fix=("Pass a Rule (e.g. StartsWith('test_')) or a function as 'rule'.",),
        verbose=False,
    )
