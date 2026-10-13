from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.rules import Rule
from simplibs.path.logic.scanners import filter_paths


class _IsPython(Rule):
    __slots__ = ()

    def is_valid(self, value) -> bool:
        return value.suffix == ".py"

    def build_exception(self, value, value_name=None, context=None) -> Exception:
        return ValueError("not python")


PATHS = [Path("b.txt"), Path("a.py"), Path("dir/c.py"), Path("d.md")]


def test_filter_paths_keeps_the_paths_satisfying_a_lambda() -> None:
    assert filter_paths(PATHS, lambda p: p.suffix == ".py") == [Path("a.py"), Path("dir/c.py")]


def test_filter_paths_keeps_the_paths_satisfying_a_rule() -> None:
    assert filter_paths(PATHS, _IsPython()) == [Path("a.py"), Path("dir/c.py")]


def test_filter_paths_preserves_the_original_order() -> None:
    assert filter_paths(PATHS, lambda p: True) == PATHS


def test_filter_paths_returns_a_new_list() -> None:
    result = filter_paths(PATHS, lambda p: True)
    assert result == PATHS and result is not PATHS


def test_filter_paths_returns_an_empty_list_when_nothing_matches() -> None:
    assert filter_paths(PATHS, lambda p: False) == []


def test_filter_paths_returns_an_empty_list_for_empty_input() -> None:
    assert filter_paths([], lambda p: True) == []


def test_filter_paths_treats_truthy_results_as_a_match() -> None:
    assert filter_paths(PATHS, lambda p: p.suffix) == PATHS


@pytest.mark.parametrize("container", [list, tuple, set, frozenset])
def test_filter_paths_accepts_collections(container) -> None:
    result = filter_paths(container(PATHS), lambda p: p.suffix == ".md")
    assert result == [Path("d.md")]


def test_filter_paths_rejects_a_generator_without_consuming_it() -> None:
    generator = (path for path in PATHS)
    with pytest.raises(ValidationError):
        filter_paths(generator, lambda p: True)
    assert next(generator) == Path("b.txt")


@pytest.mark.parametrize("bad_item", ["a.py", 5, None])
def test_filter_paths_rejects_non_path_items(bad_item) -> None:
    with pytest.raises(ValidationError):
        filter_paths([Path("a.py"), bad_item], lambda p: True)


@pytest.mark.parametrize("bad_rule", [None, 42, "suffix"])
def test_filter_paths_rejects_a_missing_or_non_callable_rule(bad_rule) -> None:
    with pytest.raises(ValidationError):
        filter_paths(PATHS, bad_rule)


def test_filter_paths_requires_a_rule() -> None:
    with pytest.raises(TypeError):
        filter_paths(PATHS)


def test_filter_paths_propagates_exceptions_from_the_predicate() -> None:
    def broken(path: Path) -> bool:
        raise RuntimeError("boom")
    with pytest.raises(RuntimeError):
        filter_paths(PATHS, broken)
