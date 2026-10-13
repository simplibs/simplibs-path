from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.exception.testing import assert_exception_function, Kwargs
from simplibs.rules import Rule
from simplibs.rules.predicates.strings import Contains
from simplibs.rules.testing import assert_rule_contract
from simplibs.path.rules import NameIs


def test_name_is_contract(subtests) -> None:
    """Verify the complete contract of the NameIs rule."""
    assert_rule_contract(
        subtests,
        rule=NameIs(Contains("test_")),
        valid_values=["test_a.py", Path("dir/test_b.py"), "x/test_", "dir/my_test_file.txt"],
        invalid_values=["a.py", "dir/test_x/a.py", "tests/b.py", "", "   ", "a\0b", None, 5, b"x"],
        expected_description="name: string containing 'test_'",
        rule_factory=NameIs,
        invalid_init_params=[
            (("not callable",), {}),
            ((None,), {}),
            ((5,), {}),
        ],
        check_value=False,  # the card is the wrapped rule's, about the extracted name
        verbose=False,
    )


def test_name_is_judges_only_the_final_name() -> None:
    rule = NameIs(Contains("data"))
    assert rule.is_valid("data/a.txt") is False
    assert rule.is_valid("a/data.txt") is True


def test_name_is_accepts_a_plain_callable() -> None:
    rule = NameIs(lambda name: name.startswith("a"))
    assert rule.is_valid("dir/apple.txt") is True
    assert rule.is_valid("dir/banana.txt") is False


def test_name_is_describe_with_a_plain_callable_uses_its_name() -> None:
    def starts_with_a(name: str) -> bool:
        return name.startswith("a")
    assert NameIs(starts_with_a).describe().startswith("name: ")
    assert "starts_with_a" in NameIs(starts_with_a).describe()


def test_name_is_describe_wraps_compound_operands_in_parentheses() -> None:
    rule = NameIs(Contains("a") | Contains("b"))
    assert rule.describe() == "name: (string containing 'a' | string containing 'b')"


def test_name_is_composes_with_other_rules() -> None:
    rule = NameIs(Contains("a")) & NameIs(Contains("b"))
    assert rule.is_valid("ab.txt") is True
    assert rule.is_valid("a.txt") is False


def test_name_is_exposes_the_wrapped_rule() -> None:
    inner = Contains("x")
    assert NameIs(inner).rule is inner


def test_name_is_card_is_the_wrapped_rules_own_for_the_name(subtests) -> None:
    rule = NameIs(Contains("test_"))
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("src/app.py", Kwargs(value_name="source", context="step")),
        exception_type=ValidationError,
        error_name="CONTAINS_ERROR",
        label="source.name",
        context="step",
        value="app.py",
        expected="string containing 'test_'",
        problem="Value 'app.py' does not contain 'test_'.",
        exception=ValueError,
        verbose=False,
    )


def test_name_is_card_without_a_value_name_uses_the_part_name(subtests) -> None:
    rule = NameIs(Contains("test_"))
    assert_exception_function(
        subtests,
        func=rule.validate,
        invalid_params=("app.py",),
        exception_type=ValidationError,
        label="name",
        value="app.py",
        verbose=False,
    )


def test_name_is_card_for_a_non_path(subtests) -> None:
    assert_exception_function(
        subtests,
        func=NameIs(Contains("x")).validate,
        invalid_params=(5, Kwargs(value_name="source")),
        exception_type=ValidationError,
        error_name="NAME_IS_ERROR",
        label="source",
        value=5,
        problem="Value 5 of type 'int' is not a string or Path.",
        how_to_fix="Provide a path as a str or a Path object.",
        exception=TypeError,
        verbose=False,
    )


def test_name_is_unreachable_fallback_when_the_name_actually_passes() -> None:
    exc = NameIs(Contains("a")).build_exception("a.txt", value_name="source")
    assert isinstance(exc, ValidationError)
    assert exc.error_name == "NAME_IS_UNREACHABLE_ERROR"
    assert exc.exception is RuntimeError


def test_name_is_rejects_a_non_callable_operand() -> None:
    with pytest.raises(ParamError):
        NameIs("Contains")
