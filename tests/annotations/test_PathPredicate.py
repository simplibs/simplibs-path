from pathlib import Path
import pytest
from simplibs.rules import IsTyping, is_integer
from simplibs.path.annotations import PathPredicate


def _named_predicate(path: Path) -> bool:
    return path.suffix == ".py"


@pytest.mark.parametrize(
    "value",
    [lambda path: True, _named_predicate, Path.is_file, is_integer],
)
def test_path_predicate_accepts_callables(value) -> None:
    """Lambdas, functions, unbound methods and Rule instances are all callable predicates."""
    assert IsTyping(PathPredicate).is_valid(value)


@pytest.mark.parametrize("value", [None, 42, "is_file", Path("a")])
def test_path_predicate_rejects_non_callables(value) -> None:
    """Anything that is not callable is rejected."""
    assert not IsTyping(PathPredicate).is_valid(value)
