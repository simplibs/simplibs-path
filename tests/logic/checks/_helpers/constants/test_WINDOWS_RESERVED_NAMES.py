from simplibs.path.logic.checks._helpers.constants import WINDOWS_RESERVED_NAMES


def test_windows_reserved_names_contents() -> None:
    """The four basic devices plus COM0-9 and LPT0-9, all upper case."""
    expected = {"CON", "PRN", "AUX", "NUL"}
    expected |= {f"COM{n}" for n in range(10)} | {f"LPT{n}" for n in range(10)}
    assert WINDOWS_RESERVED_NAMES == frozenset(expected)
    assert all(name == name.upper() for name in WINDOWS_RESERVED_NAMES)
    assert len(WINDOWS_RESERVED_NAMES) == 24


def test_windows_reserved_names_is_immutable() -> None:
    assert isinstance(WINDOWS_RESERVED_NAMES, frozenset)
