from pathlib import Path
from simplibs.rules import Rule
from simplibs.path.logic.scanners._helpers import as_path_predicate


class _IsPython(Rule):
    __slots__ = ()

    def is_valid(self, value) -> bool:
        return value.suffix == ".py"

    def build_exception(self, value, value_name=None, context=None) -> Exception:
        return ValueError("not python")


def test_as_path_predicate_unwraps_a_rule_to_is_valid() -> None:
    rule = _IsPython()
    assert as_path_predicate(rule) == rule.is_valid


def test_as_path_predicate_keeps_a_plain_function() -> None:
    def predicate(path: Path) -> bool:
        return True
    assert as_path_predicate(predicate) is predicate


def test_as_path_predicate_keeps_a_lambda() -> None:
    predicate = lambda path: False
    assert as_path_predicate(predicate) is predicate


def test_as_path_predicate_result_answers_like_the_rule() -> None:
    predicate = as_path_predicate(_IsPython())
    assert predicate(Path("a.py")) is True
    assert predicate(Path("a.txt")) is False
