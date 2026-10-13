import pytest
from simplibs.exception import NotFoundError, ParamError, StateError
from simplibs.path.logic.scanners._helpers import scan_paths
from simplibs.path.logic.scanners.ignore_names import DEFAULT_IGNORE_NAMES


def _scan(root, **overrides):
    options = dict(
        recursive=True,
        include_filter=None,
        exclude_filter=None,
        ignore_names=DEFAULT_IGNORE_NAMES,
        collect_files=True,
        collect_dirs=False,
    )
    options.update(overrides)
    return scan_paths(root, **options)


def _make_tree(root) -> None:
    (root / "a.py").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "b.py").write_text("x")
    (root / "sub" / "deep").mkdir()
    (root / "sub" / "deep" / "c.py").write_text("x")


def _names(paths) -> set[str]:
    return {path.name for path in paths}


def test_scan_paths_returns_a_lazy_iterator(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _scan(tmp_path)
    assert iter(result) is result
    assert not isinstance(result, (list, tuple, set))


def test_scan_paths_checks_the_root_when_called_not_when_iterated(tmp_path) -> None:
    with pytest.raises(NotFoundError):
        _scan(tmp_path / "missing")


def test_scan_paths_rejects_a_file_as_root_immediately(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    with pytest.raises(StateError):
        _scan(target)


def test_scan_paths_rejects_both_flags_off_immediately(tmp_path) -> None:
    with pytest.raises(ParamError):
        _scan(tmp_path, collect_files=False, collect_dirs=False)


def test_scan_paths_both_flags_off_wins_over_a_missing_root(tmp_path) -> None:
    with pytest.raises(ParamError):
        _scan(tmp_path / "missing", collect_files=False, collect_dirs=False)


def test_scan_paths_rejects_a_bare_string_for_ignore_names(tmp_path) -> None:
    with pytest.raises(ParamError):
        _scan(tmp_path, ignore_names=".git")


@pytest.mark.parametrize(
    "recursive, expected",
    [
        (True, {"a.py", "b.py", "c.py"}),
        (False, {"a.py"}),
        (0, {"a.py"}),
        (1, {"a.py", "b.py"}),
        (2, {"a.py", "b.py", "c.py"}),
    ],
)
def test_scan_paths_maps_recursive_to_a_depth(tmp_path, recursive, expected) -> None:
    _make_tree(tmp_path)
    assert _names(_scan(tmp_path, recursive=recursive)) == expected


def test_scan_paths_depth_one_is_not_mistaken_for_unlimited(tmp_path) -> None:
    """`1 == True` — the depth check must be an identity check."""
    _make_tree(tmp_path)
    assert "c.py" not in _names(_scan(tmp_path, recursive=1))


def test_scan_paths_applies_ignore_names(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _names(_scan(tmp_path, ignore_names={"deep"})) == {"a.py", "b.py"}


def test_scan_paths_applies_filters(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _names(_scan(tmp_path, include_filter=lambda p: p.name != "a.py")) == {"b.py", "c.py"}
    assert _names(_scan(tmp_path, exclude_filter=lambda p: p.name == "b.py")) == {"a.py", "c.py"}
