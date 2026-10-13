import os
from pathlib import Path
import pytest
from simplibs.path.rules._helpers import check_path


def test_check_path_returns_the_strict_bool_of_the_check(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("x")
    assert check_path(tmp_path / "a.txt", Path.is_file) is True
    assert check_path(tmp_path, Path.is_file) is False


def test_check_path_normalizes_a_truthy_non_bool_result(tmp_path) -> None:
    assert check_path(tmp_path, lambda path: 7) is True
    assert check_path(tmp_path, lambda path: 0) is False


@pytest.mark.parametrize("value", [None, 5, b"x", [], "", "   ", "a\0b"])
def test_check_path_is_false_for_a_non_path(value) -> None:
    assert check_path(value, lambda path: True) is False


def test_check_path_does_not_call_the_check_for_a_non_path() -> None:
    calls = []
    check_path(5, lambda path: calls.append(path) or True)
    assert calls == []


@pytest.mark.parametrize("error", [OSError("boom"), PermissionError("denied"), ValueError("embedded null byte")])
def test_check_path_turns_os_and_value_errors_into_false(tmp_path, error) -> None:
    def refusing(path: Path) -> bool:
        raise error
    assert check_path(tmp_path, refusing) is False


def test_check_path_does_not_hide_other_exceptions(tmp_path) -> None:
    def broken(path: Path) -> bool:
        raise RuntimeError("bug")
    with pytest.raises(RuntimeError):
        check_path(tmp_path, broken)


def test_check_path_passes_a_path_object_to_the_check(tmp_path) -> None:
    seen = []
    check_path(str(tmp_path), lambda path: seen.append(path) or True)
    assert seen == [tmp_path]


def test_check_path_expands_the_home_directory() -> None:
    seen = []
    check_path("~", lambda path: seen.append(path) or True)
    assert seen == [Path.home()]
