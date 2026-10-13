import asyncio
from pathlib import Path
import pytest
from simplibs.actions.testing import assert_action
from simplibs.exception import ParamError, ValidationError
from simplibs.path.annotations import PathLike
from simplibs.path.actions import RebasePath


def test_rebase_path_contract(subtests, tmp_path) -> None:
    """Verify the execution and construction contract of the RebasePath action."""
    source, target = tmp_path / "src", tmp_path / "out"
    action = RebasePath(source_root=source, target_root=target, new_suffix=".md")
    assert_action(
        subtests,
        action,
        valid_values=[source / "a.py", str(source / "pkg" / "b.py")],
        expected_outputs=[(target / "a.md").resolve(), (target / "pkg" / "b.md").resolve()],
        invalid_values=[5, "", tmp_path / "elsewhere" / "a.py"],
        expected_exception_type=[ValidationError, ValidationError, ParamError],
        expected_input_type=PathLike,
        expected_output_type=Path,
        action_class=RebasePath,
        invalid_init_params=[
            ((), {"source_root": "", "target_root": "out"}),
            ((), {"source_root": "src", "target_root": 5}),
            ((), {"source_root": "src", "target_root": "out", "new_suffix": 5}),
        ],
        verbose=False,
    )


def test_rebase_path_without_a_suffix_keeps_the_name(tmp_path) -> None:
    action = RebasePath(source_root=tmp_path / "s", target_root=tmp_path / "t")
    assert action(tmp_path / "s" / "a.py").name == "a.py"


def test_rebase_path_empty_suffix_removes_the_extension(tmp_path) -> None:
    action = RebasePath(source_root=tmp_path / "s", target_root=tmp_path / "t", new_suffix="")
    assert action(tmp_path / "s" / "a.py").name == "a"


def test_rebase_path_rejects_a_malformed_suffix_when_it_runs(tmp_path) -> None:
    action = RebasePath(source_root=tmp_path / "s", target_root=tmp_path / "t", new_suffix="md")
    with pytest.raises(ParamError):
        action(tmp_path / "s" / "a.py")


def test_rebase_path_requires_its_roots() -> None:
    with pytest.raises(TypeError):
        RebasePath()


def test_rebase_path_creates_nothing_on_disk(tmp_path) -> None:
    RebasePath(source_root=tmp_path / "s", target_root=tmp_path / "t")(tmp_path / "s" / "a.py")
    assert not (tmp_path / "t").exists()


def test_rebase_path_runs_asynchronously(tmp_path) -> None:
    action = RebasePath(source_root=tmp_path / "s", target_root=tmp_path / "t")
    assert asyncio.run(action.acall(tmp_path / "s" / "a.py")) == (tmp_path / "t" / "a.py").resolve()
