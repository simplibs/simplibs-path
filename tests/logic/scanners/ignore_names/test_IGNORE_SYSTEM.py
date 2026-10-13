from simplibs.path.logic.scanners.ignore_names import IGNORE_SYSTEM


def test_ignore_system_contains_os_housekeeping() -> None:
    for name in (".DS_Store", "Thumbs.db", "desktop.ini", ".Trashes", "$RECYCLE.BIN", "System Volume Information"):
        assert name in IGNORE_SYSTEM


def test_ignore_system_is_immutable() -> None:
    assert isinstance(IGNORE_SYSTEM, frozenset)
