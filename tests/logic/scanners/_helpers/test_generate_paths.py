import math
from pathlib import Path
import pytest
from simplibs.path.logic.scanners._helpers import generate_paths


def _never(name: str) -> bool:
    return False


def _generate(root: Path, *, include=None, exclude=None, files=True, dirs=False, is_ignored=_never, max_depth=math.inf):
    return list(
        generate_paths(
            root,
            max_depth=max_depth,
            is_ignored=is_ignored,
            include=include,
            exclude=exclude,
            collect_files=files,
            collect_dirs=dirs,
        )
    )


def _names(paths) -> set[str]:
    return {path.name for path in paths}


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("x")
    (root / "b.txt").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "c.py").write_text("x")


@pytest.mark.parametrize(
    "files, dirs, expected",
    [
        (True, False, {"a.py", "b.txt", "c.py"}),
        (False, True, {"sub"}),
        (True, True, {"a.py", "b.txt", "c.py", "sub"}),
        (False, False, set()),
    ],
)
def test_generate_paths_selects_by_type(tmp_path, files, dirs, expected) -> None:
    _make_tree(tmp_path)
    assert _names(_generate(tmp_path, files=files, dirs=dirs)) == expected


def test_generate_paths_include_keeps_only_accepted_paths(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _names(_generate(tmp_path, include=lambda p: p.suffix == ".py")) == {"a.py", "c.py"}


def test_generate_paths_exclude_drops_accepted_paths(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _names(_generate(tmp_path, exclude=lambda p: p.suffix == ".py")) == {"b.txt"}


def test_generate_paths_exclude_wins_over_include(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _generate(tmp_path, include=lambda p: p.suffix == ".py", exclude=lambda p: p.name == "c.py")
    assert _names(result) == {"a.py"}


def test_generate_paths_filters_receive_path_objects(tmp_path) -> None:
    _make_tree(tmp_path)
    seen = []
    _generate(tmp_path, include=lambda p: seen.append(p) or True)
    assert seen and all(isinstance(p, Path) for p in seen)


def test_generate_paths_filters_only_see_entries_of_the_selected_type(tmp_path) -> None:
    _make_tree(tmp_path)
    seen = []
    _generate(tmp_path, include=lambda p: seen.append(p.name) or True, files=True, dirs=False)
    assert "sub" not in seen


def test_generate_paths_excluding_a_directory_does_not_hide_its_children(tmp_path) -> None:
    _make_tree(tmp_path)
    result = _generate(tmp_path, exclude=lambda p: p.name == "sub", files=True, dirs=True)
    assert _names(result) == {"a.py", "b.txt", "c.py"}


def test_generate_paths_is_lazy(tmp_path) -> None:
    _make_tree(tmp_path)
    iterator = generate_paths(
        tmp_path, max_depth=math.inf, is_ignored=_never, include=None, exclude=None,
        collect_files=True, collect_dirs=False,
    )
    assert next(iterator).is_absolute()
    iterator.close()


def test_generate_paths_a_directory_symlink_counts_as_a_directory(tmp_path) -> None:
    root = tmp_path / "root"
    real = tmp_path / "real"
    root.mkdir()
    real.mkdir()
    try:
        (root / "link").symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert _names(_generate(root, files=True, dirs=False)) == set()
    assert _names(_generate(root, files=False, dirs=True)) == {"link"}
