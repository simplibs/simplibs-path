import os
from simplibs.path.logic.checks._helpers import can_create_inside


def test_can_create_inside_true_for_a_normal_directory(tmp_path) -> None:
    """A fresh temporary directory accepts new files."""
    assert can_create_inside(tmp_path) is True


def test_can_create_inside_leaves_no_trace(tmp_path) -> None:
    """The probe file is gone afterwards."""
    can_create_inside(tmp_path)
    assert list(tmp_path.iterdir()) == []


def test_can_create_inside_false_for_a_missing_directory(tmp_path) -> None:
    """Without a directory there is nothing to create inside."""
    assert can_create_inside(tmp_path / "missing") is False


def test_can_create_inside_false_when_the_target_is_a_file(tmp_path) -> None:
    """A file is not a directory."""
    target = tmp_path / "file.txt"
    target.write_text("x")
    assert can_create_inside(target) is False
