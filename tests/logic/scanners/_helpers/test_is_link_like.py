import os
import subprocess
from pathlib import Path
import pytest
from simplibs.path.logic.scanners._helpers import is_link_like


def _entry(directory: Path, name: str) -> os.DirEntry:
    with os.scandir(directory) as entries:
        return next(entry for entry in entries if entry.name == name)


def test_is_link_like_false_for_a_plain_directory(tmp_path) -> None:
    (tmp_path / "dir").mkdir()
    assert is_link_like(_entry(tmp_path, "dir")) is False


def test_is_link_like_false_for_a_plain_file(tmp_path) -> None:
    (tmp_path / "a.txt").write_text("x")
    assert is_link_like(_entry(tmp_path, "a.txt")) is False


def test_is_link_like_true_for_a_directory_symlink(tmp_path) -> None:
    (tmp_path / "real").mkdir()
    try:
        (tmp_path / "link").symlink_to(tmp_path / "real", target_is_directory=True)
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert is_link_like(_entry(tmp_path, "link")) is True


def test_is_link_like_true_for_a_file_symlink(tmp_path) -> None:
    (tmp_path / "real.txt").write_text("x")
    try:
        (tmp_path / "link.txt").symlink_to(tmp_path / "real.txt")
    except (OSError, NotImplementedError):
        pytest.skip("Creating symlinks is not permitted here.")
    assert is_link_like(_entry(tmp_path, "link.txt")) is True


@pytest.mark.skipif(os.name != "nt", reason="Junctions exist on Windows only")
def test_is_link_like_true_for_a_windows_junction(tmp_path) -> None:
    (tmp_path / "real").mkdir()
    result = subprocess.run(
        ["cmd", "/c", "mklink", "/J", str(tmp_path / "junction"), str(tmp_path / "real")],
        capture_output=True,
    )
    if result.returncode != 0:
        pytest.skip("Creating a junction failed here.")
    assert is_link_like(_entry(tmp_path, "junction")) is True
