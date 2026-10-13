import pytest
from simplibs.exception import StateError, ValidationError
from simplibs.path.logic.ensure import ensure_parent_dir


def test_ensure_parent_dir_creates_the_parent_but_not_the_path(tmp_path) -> None:
    target = tmp_path / "out" / "pkg" / "a.md"
    result = ensure_parent_dir(target)
    assert (tmp_path / "out" / "pkg").is_dir()
    assert not target.exists()
    assert result == target.resolve()


def test_ensure_parent_dir_returns_the_path_itself_not_its_parent(tmp_path) -> None:
    target = tmp_path / "x" / "file.txt"
    assert ensure_parent_dir(target).name == "file.txt"


def test_ensure_parent_dir_accepts_an_existing_parent(tmp_path) -> None:
    (tmp_path / "keep.txt").write_text("content")
    ensure_parent_dir(tmp_path / "new.txt")
    assert (tmp_path / "keep.txt").read_text() == "content"
    assert not (tmp_path / "new.txt").exists()


def test_ensure_parent_dir_leaves_an_existing_path_alone(tmp_path) -> None:
    target = tmp_path / "exists.txt"
    target.write_text("content")
    assert ensure_parent_dir(target) == target.resolve()
    assert target.read_text() == "content"


def test_ensure_parent_dir_works_with_relative_paths(tmp_path, monkeypatch) -> None:
    monkeypatch.chdir(tmp_path)
    result = ensure_parent_dir("deep/er/file.txt")
    assert (tmp_path / "deep" / "er").is_dir()
    assert result == (tmp_path / "deep" / "er" / "file.txt").resolve()


def test_ensure_parent_dir_is_idempotent(tmp_path) -> None:
    target = tmp_path / "a" / "b.txt"
    assert ensure_parent_dir(target) == ensure_parent_dir(target)


def test_ensure_parent_dir_names_a_file_in_the_parent_chain(tmp_path) -> None:
    blocker = tmp_path / "blocker"
    blocker.write_text("x")
    with pytest.raises(StateError):
        ensure_parent_dir(blocker / "new.txt")


@pytest.mark.parametrize("value", ["", "   ", None, 5])
def test_ensure_parent_dir_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        ensure_parent_dir(value)
