import pytest
from simplibs.path.logic.checks._helpers._find_length_problem import _find_length_problem


@pytest.mark.parametrize("windows, posix", [(True, True), (True, False), (False, True)])
def test_find_length_problem_accepts_255_ascii(windows, posix) -> None:
    """The limit itself is allowed."""
    assert _find_length_problem("a" * 255, windows=windows, posix=posix) is None


@pytest.mark.parametrize("windows, posix", [(True, True), (True, False), (False, True)])
def test_find_length_problem_rejects_256_ascii(windows, posix) -> None:
    """One character over the limit fails under every applicable rule set."""
    assert _find_length_problem("a" * 256, windows=windows, posix=posix) is not None


def test_find_length_problem_counts_bytes_on_posix() -> None:
    """128 two-byte characters are 256 bytes — too long for POSIX, fine for Windows."""
    name = "é" * 128
    assert _find_length_problem(name, windows=False, posix=True) is not None
    assert _find_length_problem(name, windows=True, posix=False) is None


def test_find_length_problem_counts_utf16_units_on_windows() -> None:
    """An astral character is two UTF-16 units but four UTF-8 bytes."""
    name = "😀" * 128
    assert _find_length_problem(name, windows=True, posix=False) is not None
    assert _find_length_problem("😀" * 127, windows=True, posix=False) is None


def test_find_length_problem_with_no_platform_selected_accepts_anything() -> None:
    """With neither rule set applied, nothing is checked."""
    assert _find_length_problem("a" * 1000, windows=False, posix=False) is None


def test_find_length_problem_does_not_raise_on_lone_surrogates() -> None:
    """Undecodable POSIX names (lone surrogates) are measured, not rejected by accident."""
    assert _find_length_problem("a\udc80b", windows=True, posix=True) is None
