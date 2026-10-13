import pytest
from simplibs.exception import ValidationError
from simplibs.path.logic.checks import is_valid_filename


@pytest.mark.parametrize("name", ["report.txt", ".bashrc", "archive.tar.gz", "ěščř.md"])
def test_is_valid_filename_accepts_good_names(name) -> None:
    assert is_valid_filename(name) is True


@pytest.mark.parametrize("name", ["", "a/b", "a:b", "con", "name.", "a" * 256, ".", ".."])
def test_is_valid_filename_rejects_bad_names(name) -> None:
    assert is_valid_filename(name) is False


def test_is_valid_filename_non_portable_still_rejects_universal_problems() -> None:
    assert is_valid_filename("a/b", portable=False) is False
    assert is_valid_filename("report.txt", portable=False) is True


@pytest.mark.parametrize("value", [None, 5, b"x", ["a"]])
def test_is_valid_filename_rejects_non_strings(value) -> None:
    """The annotation allows only strings."""
    with pytest.raises(ValidationError):
        is_valid_filename(value)


def test_is_valid_filename_validation_can_be_bypassed() -> None:
    """With the reserved bypass switch, the argument type is not checked."""
    with pytest.raises(AttributeError):
        is_valid_filename(5, _validate_call=False)
