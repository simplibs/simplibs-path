from simplibs.path.logic.checks._helpers.constants import WINDOWS_FORBIDDEN_CHARS


def test_windows_forbidden_chars_contents() -> None:
    """The set holds exactly the characters NTFS rejects (separators are handled elsewhere)."""
    assert WINDOWS_FORBIDDEN_CHARS == frozenset('<>:"|?*')
    assert "/" not in WINDOWS_FORBIDDEN_CHARS
    assert "\\" not in WINDOWS_FORBIDDEN_CHARS


def test_windows_forbidden_chars_is_immutable() -> None:
    assert isinstance(WINDOWS_FORBIDDEN_CHARS, frozenset)
