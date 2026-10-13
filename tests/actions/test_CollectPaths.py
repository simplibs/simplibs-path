import asyncio
from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import NotFoundError, ParamError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import CollectPaths


def _make_tree(root: Path) -> None:
    (root / "a.py").write_text("x")
    (root / "sub").mkdir()
    (root / "sub" / "b.txt").write_text("x")
    (root / ".git").mkdir()
    (root / ".git" / "config").write_text("x")


def test_collect_paths_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the CollectPaths action."""
    _make_tree(tmp_path)
    base = tmp_path.resolve()
    assert_action(
        subtests,
        CollectPaths(collect_dirs=True),
        valid_values=[tmp_path, str(tmp_path)],
        expected_outputs=[
            [base / "a.py", base / "sub", base / "sub" / "b.txt"],
            [base / "a.py", base / "sub", base / "sub" / "b.txt"],
        ],
        invalid_values=[5, "", tmp_path / "missing"],
        expected_exception_type=[ValidationError, ValidationError, NotFoundError],
        expected_input_type=PathLike,
        expected_output_type=list[Path],
        action_class=CollectPaths,
        invalid_init_params=[
            ((), {"collect_files": "yes"}),
            ((), {"recursive": -1}),
            ((), {"include_filter": 5}),
            ((), {"ignore_names": 5}),
        ],
        verbose=False,
    )


def test_collect_paths_defaults_collect_files_only(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in CollectPaths()(tmp_path)] == ["a.py", "b.txt"]


def test_collect_paths_options_are_stored_per_instance(tmp_path) -> None:
    _make_tree(tmp_path)
    shallow = CollectPaths(recursive=False)
    deep = CollectPaths()
    assert [p.name for p in shallow(tmp_path)] == ["a.py"]
    assert [p.name for p in deep(tmp_path)] == ["a.py", "b.txt"]


def test_collect_paths_filters_and_ignore_names(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in CollectPaths(include_filter=lambda p: p.suffix == ".py")(tmp_path)] == ["a.py"]
    assert "config" in {p.name for p in CollectPaths(ignore_names=None)(tmp_path)}


def test_collect_paths_both_flags_off_raises_when_it_runs(tmp_path) -> None:
    with pytest.raises(ParamError):
        CollectPaths(collect_files=False, collect_dirs=False)(tmp_path)


def test_collect_paths_rejects_a_bare_string_for_ignore_names_when_it_runs(tmp_path) -> None:
    with pytest.raises(ParamError):
        CollectPaths(ignore_names=".git")(tmp_path)


def test_collect_paths_runs_asynchronously(tmp_path) -> None:
    _make_tree(tmp_path)
    assert [p.name for p in asyncio.run(CollectPaths().acall(tmp_path))] == ["a.py", "b.txt"]
