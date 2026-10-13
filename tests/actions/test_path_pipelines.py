import asyncio
from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.path.actions import (
    ChangeSuffix,
    CollectDirs,
    CollectFiles,
    CollectPaths,
    EnsureDir,
    EnsureParentDir,
    FilterPaths,
    MakeUniquePath,
    NormalizePath,
    RebasePath,
    RelativizePath,
)
from simplibs.path.rules import HasSuffix, IsDir, IsHidden


def _make_project(root: Path) -> None:
    (root / "src").mkdir()
    (root / "src" / "a.py").write_text("x")
    (root / "src" / "b.md").write_text("x")
    (root / "src" / ".secret.py").write_text("x")
    (root / "src" / "pkg").mkdir()
    (root / "src" / "pkg" / "c.py").write_text("x")


def test_a_rule_guards_the_head_of_a_pipeline(tmp_path) -> None:
    _make_project(tmp_path)
    pipeline = IsDir() >> CollectFiles(include_filter=HasSuffix(".py")) >> FilterPaths(rule=~IsHidden())
    result = pipeline(tmp_path / "src")
    assert [p.name for p in result] == ["a.py", "c.py"]


def test_the_guard_rejects_a_non_directory_before_anything_runs(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    with pytest.raises(ValidationError):
        (IsDir() >> CollectFiles())(target)


def test_normalize_then_ensure_then_collect(tmp_path) -> None:
    pipeline = NormalizePath() >> EnsureDir() >> CollectFiles()
    assert pipeline(tmp_path / "a" / ".." / "new") == []
    assert (tmp_path / "new").is_dir()


def test_mirroring_a_tree_with_rebase_and_ensure_parent(tmp_path) -> None:
    _make_project(tmp_path)
    source, target = tmp_path / "src", tmp_path / "out"
    rebase = RebasePath(source_root=source, target_root=target, new_suffix=".txt") >> EnsureParentDir()
    outputs = [rebase(path) for path in CollectFiles(include_filter=HasSuffix(".py"))(source)]
    relative = [p.relative_to(target.resolve()).as_posix() for p in outputs]
    assert relative == [".secret.txt", "a.txt", "pkg/c.txt"]
    assert (target / "pkg").is_dir()
    assert not (target / "pkg" / "c.txt").exists()


def test_rebase_then_make_unique_never_overwrites(tmp_path) -> None:
    (tmp_path / "s").mkdir()
    (tmp_path / "t").mkdir()
    (tmp_path / "t" / "a.txt").write_text("existing")
    step = RebasePath(source_root=tmp_path / "s", target_root=tmp_path / "t") >> MakeUniquePath()
    assert step(tmp_path / "s" / "a.txt").name == "a (1).txt"


def test_relativize_a_collection_of_collected_paths(tmp_path) -> None:
    _make_project(tmp_path)
    relativize = RelativizePath(root=tmp_path / "src")
    names = [relativize(p).as_posix() for p in CollectFiles()(tmp_path / "src")]
    assert "a.py" in names and "pkg/c.py" in names


def test_two_collectors_run_in_parallel_over_the_same_root(tmp_path) -> None:
    _make_project(tmp_path)
    files, dirs = (CollectFiles() & CollectDirs())(tmp_path / "src")
    assert [p.name for p in files] == [".secret.py", "a.py", "b.md", "c.py"]
    assert [p.name for p in dirs] == ["pkg"]


def test_change_suffix_composes_into_a_pipeline() -> None:
    assert (NormalizePath(resolve_symlinks=False) >> ChangeSuffix(new_suffix=".md"))("dir/report.txt").name == "report.md"


def test_a_whole_pipeline_runs_asynchronously(tmp_path) -> None:
    _make_project(tmp_path)
    pipeline = NormalizePath() >> CollectPaths() >> FilterPaths(rule=HasSuffix(".md"))
    result = asyncio.run(pipeline.acall(tmp_path / "src"))
    assert [p.name for p in result] == ["b.md"]
