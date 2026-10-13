from pathlib import Path
import pytest
from simplibs.exception import ValidationError
from simplibs.path.logic.checks import is_within


def _symlink_or_skip(link: Path, target: Path) -> None:
    try:
        link.symlink_to(target, target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")


def test_is_within_true_for_a_nested_path(tmp_path) -> None:
    assert is_within(tmp_path / "a" / "b.txt", tmp_path) is True


def test_is_within_true_for_a_path_that_does_not_exist(tmp_path) -> None:
    assert is_within(tmp_path / "no" / "such" / "file", tmp_path) is True


def test_is_within_equal_path_depends_on_allow_equal(tmp_path) -> None:
    assert is_within(tmp_path, tmp_path) is True
    assert is_within(tmp_path, tmp_path, allow_equal=False) is False


def test_is_within_false_for_an_outside_path(tmp_path) -> None:
    assert is_within(tmp_path / "other" / "a.txt", tmp_path / "src") is False


def test_is_within_false_for_a_sibling_with_a_common_prefix(tmp_path) -> None:
    """'src2' is not inside 'src' even though the string starts with it."""
    assert is_within(tmp_path / "src2" / "a.txt", tmp_path / "src") is False


def test_is_within_false_when_parent_references_escape_the_root(tmp_path) -> None:
    assert is_within(tmp_path / "src" / ".." / "secret.txt", tmp_path / "src") is False


def test_is_within_true_when_parent_references_stay_inside(tmp_path) -> None:
    assert is_within(tmp_path / "src" / "a" / ".." / "b.txt", tmp_path / "src") is True


def test_is_within_resolves_a_symlink_that_points_outside(tmp_path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    _symlink_or_skip(root / "escape", outside)
    assert is_within(root / "escape" / "file.txt", root) is False


def test_is_within_lexical_mode_trusts_the_symlink_name(tmp_path) -> None:
    root = tmp_path / "root"
    outside = tmp_path / "outside"
    root.mkdir()
    outside.mkdir()
    _symlink_or_skip(root / "escape", outside)
    assert is_within(root / "escape" / "file.txt", root, resolve_symlinks=False) is True


def test_is_within_accepts_strings(tmp_path) -> None:
    assert is_within(str(tmp_path / "a.txt"), str(tmp_path)) is True


@pytest.mark.parametrize("value", ["", None, 5])
def test_is_within_rejects_invalid_input(tmp_path, value) -> None:
    with pytest.raises(ValidationError):
        is_within(value, tmp_path)
    with pytest.raises(ValidationError):
        is_within(tmp_path, value)


def test_is_within_false_for_a_null_byte(tmp_path) -> None:
    assert is_within("a\0b", tmp_path) is False
    assert is_within(tmp_path, "a\0b") is False
