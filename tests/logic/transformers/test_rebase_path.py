from pathlib import Path
import pytest
from simplibs.exception import ParamError, ValidationError
from simplibs.path.logic.transformers import rebase_path


def test_rebase_path_maps_between_roots(tmp_path) -> None:
    """The structure below the source root is kept under the target root."""
    result = rebase_path(
        tmp_path / "src" / "pkg" / "a.py",
        source_root=tmp_path / "src",
        target_root=tmp_path / "out",
    )
    assert result == (tmp_path / "out" / "pkg" / "a.py").resolve()


def test_rebase_path_root_itself_maps_to_target_root(tmp_path) -> None:
    """The source root maps to the target root."""
    result = rebase_path(tmp_path / "src", source_root=tmp_path / "src", target_root=tmp_path / "out")
    assert result == (tmp_path / "out").resolve()


def test_rebase_path_can_change_suffix(tmp_path) -> None:
    """With new_suffix, the extension of the result is replaced."""
    result = rebase_path(
        tmp_path / "src" / "a.py",
        source_root=tmp_path / "src",
        target_root=tmp_path / "out",
        new_suffix=".md",
    )
    assert result == (tmp_path / "out" / "a.md").resolve()


def test_rebase_path_empty_suffix_removes_extension(tmp_path) -> None:
    """An empty new_suffix removes the extension; None keeps it."""
    kept = rebase_path(tmp_path / "s" / "a.py", source_root=tmp_path / "s", target_root=tmp_path / "t")
    removed = rebase_path(
        tmp_path / "s" / "a.py", source_root=tmp_path / "s", target_root=tmp_path / "t", new_suffix=""
    )
    assert kept.name == "a.py"
    assert removed.name == "a"


def test_rebase_path_creates_nothing_on_disk(tmp_path) -> None:
    """Rebasing is pure path arithmetic."""
    rebase_path(tmp_path / "s" / "a.py", source_root=tmp_path / "s", target_root=tmp_path / "t")
    assert not (tmp_path / "t").exists()


def test_rebase_path_works_with_relative_inputs(tmp_path, monkeypatch) -> None:
    """Relative paths are all interpreted against the working directory."""
    monkeypatch.chdir(tmp_path)
    result = rebase_path("src/a.py", source_root="src", target_root="out")
    assert result == (tmp_path / "out" / "a.py").resolve()


def test_rebase_path_rejects_path_outside_source_root(tmp_path) -> None:
    """A path outside the source root cannot be rebased."""
    with pytest.raises(ParamError):
        rebase_path(tmp_path / "elsewhere" / "a.py", source_root=tmp_path / "src", target_root=tmp_path / "out")


@pytest.mark.parametrize("bad_suffix", ["md", ".", "/x"])
def test_rebase_path_rejects_malformed_suffix(tmp_path, bad_suffix) -> None:
    """A malformed new_suffix is reported."""
    with pytest.raises(ParamError):
        rebase_path(
            tmp_path / "s" / "a.py",
            source_root=tmp_path / "s",
            target_root=tmp_path / "t",
            new_suffix=bad_suffix,
        )


def test_rebase_path_rejects_invalid_arguments(tmp_path) -> None:
    """Blank paths and a non-string suffix are rejected by the annotations."""
    with pytest.raises(ValidationError):
        rebase_path("", source_root=tmp_path, target_root=tmp_path)
    with pytest.raises(ValidationError):
        rebase_path(tmp_path, source_root="", target_root=tmp_path)
    with pytest.raises(ValidationError):
        rebase_path(tmp_path, source_root=tmp_path, target_root=tmp_path, new_suffix=5)
