from pathlib import Path
import pytest
from simplibs.path.logic.scanners._helpers import ScanEntry


def test_scan_entry_holds_path_and_kind() -> None:
    entry = ScanEntry(Path("a.txt"), True, False)
    assert entry.path == Path("a.txt")
    assert entry.is_file is True
    assert entry.is_dir is False


def test_scan_entry_unpacks_like_a_tuple() -> None:
    path, is_file, is_dir = ScanEntry(Path("d"), False, True)
    assert (path, is_file, is_dir) == (Path("d"), False, True)


def test_scan_entry_is_immutable() -> None:
    entry = ScanEntry(Path("a"), True, False)
    with pytest.raises(AttributeError):
        entry.is_file = False
