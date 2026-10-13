import pytest
from simplibs.exception import ValidationError
from simplibs.path.logic.checks import is_empty_dir


def test_is_empty_dir_true_for_an_empty_directory(tmp_path) -> None:
    assert is_empty_dir(tmp_path) is True


def test_is_empty_dir_false_when_it_has_a_file(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("x")
    assert is_empty_dir(tmp_path) is False


def test_is_empty_dir_false_when_it_has_only_a_subdirectory(tmp_path) -> None:
    (tmp_path / "sub").mkdir()
    assert is_empty_dir(tmp_path) is False


def test_is_empty_dir_false_for_a_file(tmp_path) -> None:
    target = tmp_path / "a.txt"
    target.write_text("x")
    assert is_empty_dir(target) is False


def test_is_empty_dir_false_for_a_missing_path(tmp_path) -> None:
    assert is_empty_dir(tmp_path / "missing") is False


def test_is_empty_dir_accepts_a_string(tmp_path) -> None:
    assert is_empty_dir(str(tmp_path)) is True


@pytest.mark.parametrize("value", ["", None, 5])
def test_is_empty_dir_rejects_invalid_input(value) -> None:
    with pytest.raises(ValidationError):
        is_empty_dir(value)


def test_is_empty_dir_false_for_a_null_byte() -> None:
    assert is_empty_dir("a\0b") is False
