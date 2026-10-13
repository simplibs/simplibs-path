from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.path.rules._helpers import build_not_a_path_exception


def _build(value):
    return build_not_a_path_exception(
        error_name="SOME_ERROR",
        expected="a path",
        value=value,
        value_name="source",
        context="step",
    )


@pytest.mark.parametrize("value", [5, None, b"x", [], 1.5])
def test_non_string_values_give_a_type_error_card(value) -> None:
    exc = _build(value)
    assert isinstance(exc, ValidationError)
    assert exc.exception is TypeError
    assert exc.problem == f"Value {value!r} of type '{type(value).__name__}' is not a string or Path."
    assert exc.how_to_fix == "Provide a path as a str or a Path object."


@pytest.mark.parametrize("value", ["", "   ", "a\0b", Path("a\0b")])
def test_unusable_strings_give_a_value_error_card(value) -> None:
    exc = _build(value)
    assert exc.exception is ValueError
    assert exc.problem == f"Value {value!r} cannot be used as a path (it is blank or contains a null byte)."
    assert exc.how_to_fix == "Provide a non-blank path without null bytes."


def test_the_card_carries_the_given_metadata() -> None:
    exc = _build(5)
    assert exc.error_name == "SOME_ERROR"
    assert exc.label == "source"
    assert exc.context == "step"
    assert exc.expected == "a path"
    assert exc.value == 5
