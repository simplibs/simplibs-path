import math
import os
import subprocess
from pathlib import Path
import pytest
from simplibs.path.logic.scanners._helpers import walk_tree


def _never(name: str) -> bool:
    return False


def _walk(root: Path, *, max_depth=math.inf, is_ignored=_never):
    return list(walk_tree(root, max_depth=max_depth, is_ignored=is_ignored))


def _relative(entries, root: Path) -> set[str]:
    return {entry.path.relative_to(root).as_posix() for entry in entries}


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "b.py").write_text("x")
    (root / "sub" / "deep").mkdir()
    (root / "sub" / "deep" / "c.md").write_text("x")


def test_walk_tree_yields_every_file_and_directory(tmp_path) -> None:
    _make_tree(tmp_path)
    assert _relative(_walk(tmp_path), tmp_path) == {"a.py", "sub", "sub/b.py", "sub/deep", "sub/deep/c.md"}


def test_walk_tree_reports_the_kind_of_each_entry(tmp_path) -> None:
    _make_tree(tmp_path)
    kinds = {e.path.relative_to(tmp_path).as_posix(): (e.is_file, e.is_dir) for e in _walk(tmp_path)}
    assert kinds["a.py"] == (True, False)
    assert kinds["sub"] == (False, True)


def test_walk_tree_yields_absolute_paths_below_the_root(tmp_path) -> None:
    _make_tree(tmp_path)
    for entry in _walk(tmp_path):
        assert entry.path.is_absolute()
        assert entry.path.is_relative_to(tmp_path)


def test_walk_tree_does_not_yield_the_root_itself(tmp_path) -> None:
    assert _walk(tmp_path) == []


@pytest.mark.parametrize(
    "max_depth, expected",
    [
        (0, {"a.py", "sub"}),
        (1, {"a.py", "sub", "sub/b.py", "sub/deep"}),
        (2, {"a.py", "sub", "sub/b.py", "sub/deep", "sub/deep/c.md"}),
        (math.inf, {"a.py", "sub", "sub/b.py", "sub/deep", "sub/deep/c.md"}),
    ],
)
def test_walk_tree_respects_the_depth_limit(tmp_path, max_depth, expected) -> None:
    _make_tree(tmp_path)
    assert _relative(_walk(tmp_path, max_depth=max_depth), tmp_path) == expected


def test_walk_tree_skips_ignored_files_and_directories(tmp_path) -> None:
    _make_tree(tmp_path)
    (tmp_path / "Thumbs.db").write_text("x")
    entries = _walk(tmp_path, is_ignored=lambda name: name in {"deep", "Thumbs.db"})
    assert _relative(entries, tmp_path) == {"a.py", "sub", "sub/b.py"}


def test_walk_tree_does_not_enter_an_ignored_directory(tmp_path) -> None:
    (tmp_path / ".git").mkdir()
    (tmp_path / ".git" / "config").write_text("x")
    (tmp_path / "keep.txt").write_text("x")
    assert _relative(_walk(tmp_path, is_ignored=lambda name: name == ".git"), tmp_path) == {"keep.txt"}


def test_walk_tree_asks_about_names_not_paths(tmp_path) -> None:
    _make_tree(tmp_path)
    asked = []
    _walk(tmp_path, is_ignored=lambda name: asked.append(name) or False)
    assert "a.py" in asked and all("/" not in n and "\\" not in n for n in asked)


def test_walk_tree_does_not_enter_a_symlinked_directory(tmp_path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (real / "inside.txt").write_text("x")
    root = tmp_path / "root"
    root.mkdir()
    try:
        (root / "link").symlink_to(real, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    entries = _walk(root)
    assert _relative(entries, root) == {"link"}
    assert entries[0].is_dir is True


def test_walk_tree_survives_a_symlink_cycle(tmp_path) -> None:
    (tmp_path / "dir").mkdir()
    try:
        (tmp_path / "dir" / "loop").symlink_to(tmp_path, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert _relative(_walk(tmp_path), tmp_path) == {"dir", "dir/loop"}


def test_walk_tree_yields_a_file_symlink_as_a_file(tmp_path) -> None:
    root = tmp_path / "root"
    root.mkdir()
    (tmp_path / "real.txt").write_text("x")
    try:
        (root / "link.txt").symlink_to(tmp_path / "real.txt")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    entries = _walk(root)
    assert [(e.path.name, e.is_file, e.is_dir) for e in entries] == [("link.txt", True, False)]


def test_walk_tree_does_not_yield_a_broken_symlink(tmp_path) -> None:
    try:
        (tmp_path / "dangling").symlink_to(tmp_path / "nowhere")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert _walk(tmp_path) == []


@pytest.mark.skipif(not hasattr(os, "mkfifo"), reason="FIFOs exist on POSIX only")
def test_walk_tree_does_not_yield_special_files(tmp_path) -> None:
    os.mkfifo(tmp_path / "pipe")
    (tmp_path / "regular.txt").write_text("x")
    assert _relative(_walk(tmp_path), tmp_path) == {"regular.txt"}


@pytest.mark.skipif(os.name == "nt" or (hasattr(os, "geteuid") and os.geteuid() == 0), reason="Needs POSIX permissions and a non-root user")
def test_walk_tree_skips_an_unreadable_directory_and_continues(tmp_path) -> None:
    (tmp_path / "locked").mkdir()
    (tmp_path / "locked" / "hidden.txt").write_text("x")
    (tmp_path / "open").mkdir()
    (tmp_path / "open" / "visible.txt").write_text("x")
    (tmp_path / "locked").chmod(0o000)
    try:
        assert _relative(_walk(tmp_path), tmp_path) == {"locked", "open", "open/visible.txt"}
    finally:
        (tmp_path / "locked").chmod(0o755)


def test_walk_tree_returns_nothing_for_a_missing_root(tmp_path) -> None:
    """The walker itself never raises — root checks belong to resolve_scan_root."""
    assert _walk(tmp_path / "missing") == []


def test_walk_tree_is_lazy(tmp_path) -> None:
    _make_tree(tmp_path)
    iterator = walk_tree(tmp_path, max_depth=math.inf, is_ignored=_never)
    assert next(iterator) is not None
    iterator.close()


@pytest.mark.skipif(os.name != "nt", reason="Junctions exist on Windows only")
def test_walk_tree_does_not_enter_a_windows_junction(tmp_path) -> None:
    real = tmp_path / "real"
    real.mkdir()
    (real / "inside.txt").write_text("x")
    root = tmp_path / "root"
    root.mkdir()
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(root / "junction"), str(real)],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("Creating a junction failed here.")
    assert _relative(_walk(root), root) == {"junction"}
