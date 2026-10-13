import pytest
from simplibs.exception import NotFoundError, ParamError, StateError, ValidationError
from simplibs.path.logic.scanners import collect_paths, iter_paths


def _make_tree(root) -> None:
    (root / "a.py").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "b.py").write_text("x")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("x")


def test_iter_paths_returns_a_lazy_iterator_not_a_list(tmp_path) -> None:
    _make_tree(tmp_path)
    result = iter_paths(tmp_path)
    assert iter(result) is result
    assert not isinstance(result, (list, tuple, set))


def test_iter_paths_yields_the_same_paths_as_collect_paths(tmp_path) -> None:
    _make_tree(tmp_path)
    assert sorted(iter_paths(tmp_path)) == collect_paths(tmp_path)
    assert sorted(iter_paths(tmp_path, collect_dirs=True)) == collect_paths(tmp_path, collect_dirs=True)


def test_iter_paths_yields_absolute_paths(tmp_path) -> None:
    _make_tree(tmp_path)
    assert all(path.is_absolute() for path in iter_paths(tmp_path))


def test_iter_paths_can_be_stopped_early(tmp_path) -> None:
    _make_tree(tmp_path)
    iterator = iter_paths(tmp_path)
    assert next(iterator).is_absolute()
    iterator.close()


def test_iter_paths_is_exhausted_after_one_pass(tmp_path) -> None:
    _make_tree(tmp_path)
    iterator = iter_paths(tmp_path)
    assert len(list(iterator)) == 2
    assert list(iterator) == []


def test_iter_paths_supports_filters_depth_and_ignore_names(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in iter_paths(tmp_path, recursive=False)] == ["a.py"]
    assert {p.name for p in iter_paths(tmp_path, include_filter=lambda p: p.name == "b.py")} == {"b.py"}
    assert ".git" not in {p.parent.name for p in iter_paths(tmp_path)}
    assert "config" in {p.name for p in iter_paths(tmp_path, ignore_names=None)}


def test_iter_paths_checks_the_root_at_the_call_not_at_the_first_next(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        iter_paths(tmp_path / "missing")


def test_iter_paths_rejects_a_file_as_root_at_the_call(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    with pytest.raises(StateError):
        iter_paths(target)


def test_iter_paths_rejects_both_flags_off_at_the_call(tmp_path) -> None:
    with pytest.raises(ParamError):
        iter_paths(tmp_path, collect_files=False, collect_dirs=False)


def test_iter_paths_rejects_a_bare_string_for_ignore_names_at_the_call(tmp_path) -> None:
    with pytest.raises(ParamError):
        iter_paths(tmp_path, ignore_names=".git")


@pytest.mark.parametrize("value", ["", None, 5])
def test_iter_paths_rejects_an_invalid_root(value) -> None:
    with pytest.raises(ValidationError):
        iter_paths(value)
