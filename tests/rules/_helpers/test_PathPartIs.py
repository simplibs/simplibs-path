from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.rules import Rule
from simplibs.rules.predicates.strings import Contains
from simplibs.path.rules._helpers import PathPartIs


class _Extension(PathPartIs):
    """A minimal lens for the test: the whole path text."""
    __slots__ = ()
    _part_name = "text"

    @staticmethod
    def _get_part(path: Path) -> str:
        return path.as_posix()


def test_the_base_class_requires_a_subclass_to_define_the_part() -> None:
    with pytest.raises(NotImplementedError):
        PathPartIs._get_part(Path("a"))


def test_a_subclass_works_with_a_rule() -> None:
    rule = _Extension(Contains("src/"))
    assert rule.is_valid("src/a.py") is True
    assert rule.is_valid("lib/a.py") is False
    assert rule.describe() == "text: string containing 'src/'"


def test_a_plain_callable_is_wrapped_into_a_rule() -> None:
    rule = _Extension(lambda text: "a" in text)
    assert isinstance(rule.rule, Rule)
    assert rule.is_valid("a.txt") is True
    assert rule.is_valid("b.txt") is False


def test_a_rule_operand_is_kept_as_it_is() -> None:
    inner = Contains("x")
    assert _Extension(inner).rule is inner


@pytest.mark.parametrize("bad", ["text", None, 5, []])
def test_a_non_callable_operand_is_a_param_error(bad) -> None:
    with pytest.raises(ParamError):
        _Extension(bad)


def test_instances_have_no_dict() -> None:
    assert not hasattr(_Extension(Contains("x")), "__dict__")


def test_the_card_error_name_is_derived_from_the_part_name() -> None:
    exc = _Extension(Contains("x")).build_exception(5)
    assert isinstance(exc, ValidationError)
    assert exc.error_name == "TEXT_IS_ERROR"


def test_a_faulty_describe_of_the_operand_falls_back_to_its_class_name() -> None:
    class _BrokenDescribe(Rule):
        __slots__ = ()

        def is_valid(self, value) -> bool:
            return True

        def build_exception(self, value, value_name=None, context=None) -> Exception:
            return ValueError()

        def describe(self) -> str:
            raise RuntimeError("broken")

    assert _Extension(_BrokenDescribe()).describe() == "text: _BrokenDescribe"
