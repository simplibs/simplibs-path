import pytest
from simplibs.exception import ValidationError
from simplibs.path.rules._helpers import build_path_rule_exception


def _build(value, **overrides):
    options = dict(
        error_name="SOME_ERROR",
        expected="a thing",
        value=value,
        value_name="source",
        context="step",
        problem="It is wrong.",
        how_to_fix="Fix it.",
    )
    options.update(overrides)
    return build_path_rule_exception(**options)


def test_a_usable_path_gets_the_rules_own_sentences(tmp_path) -> None:
    exc = _build(tmp_path)
    assert isinstance(exc, ValidationError)
    assert exc.error_name == "SOME_ERROR"
    assert exc.label == "source"
    assert exc.context == "step"
    assert exc.expected == "a thing"
    assert exc.problem == "It is wrong."
    assert exc.how_to_fix == "Fix it."
    assert exc.value == tmp_path
    assert exc.exception is ValueError


def test_the_wrapped_exception_type_can_be_changed(tmp_path) -> None:
    assert _build(tmp_path, exception=PermissionError).exception is PermissionError


@pytest.mark.parametrize("value", [5, None, [], "", "   ", "a\0b"])
def test_an_unusable_value_gets_the_shared_not_a_path_card(value) -> None:
    exc = _build(value)
    assert exc.error_name == "SOME_ERROR"
    assert exc.expected == "a thing"
    assert exc.problem != "It is wrong."
    assert exc.how_to_fix != "Fix it."
    assert exc.value == value or exc.value is value


def test_all_arguments_are_keyword_only(tmp_path) -> None:
    with pytest.raises(TypeError):
        build_path_rule_exception("E", "expected", tmp_path, "name", "ctx", "p", "f")
