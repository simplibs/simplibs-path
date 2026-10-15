"""Tests: the list-returning scanner actions log like every other action — with large values shortened."""

import logging

from simplibs.path.actions import CollectDirs, CollectFiles, CollectPaths, FilterPaths


def _make_files(root, count=30):
    for index in range(count):
        (root / f"f{index:02d}.txt").write_text("x")


def _make_dirs(root, count=30):
    for index in range(count):
        (root / f"d{index:02d}").mkdir()


# The records are captured at the ROOT logger on purpose: it does not depend on which logger name the
# generated action logs under, only on the fact that it logs at all.

def test_collect_files_logs_a_shortened_result(tmp_path, caplog):
    """Verify CollectFiles logs, and a 30-item result is written as a short record."""
    _make_files(tmp_path)

    with caplog.at_level(logging.DEBUG):
        result = CollectFiles()(tmp_path)

    assert len(result) == 30
    assert "(30 items)" in caplog.text
    assert "f29.txt" not in caplog.text          # only the first items are written
    assert len(caplog.text) < 5000


def test_collect_paths_logs_a_shortened_result(tmp_path, caplog):
    """Verify CollectPaths logs, and a 30-item result is written as a short record."""
    _make_files(tmp_path)

    with caplog.at_level(logging.DEBUG):
        result = CollectPaths()(tmp_path)

    assert len(result) == 30
    assert "(30 items)" in caplog.text
    assert "f29.txt" not in caplog.text


def test_collect_dirs_logs_a_shortened_result(tmp_path, caplog):
    """Verify CollectDirs logs, and a 30-item result is written as a short record."""
    _make_dirs(tmp_path)

    with caplog.at_level(logging.DEBUG):
        result = CollectDirs()(tmp_path)

    assert len(result) == 30
    assert "(30 items)" in caplog.text
    assert "d29" not in caplog.text


def test_filter_paths_logs_shortened_input_and_result(tmp_path, caplog):
    """Verify FilterPaths shortens a large INPUT list as well as the result."""
    _make_files(tmp_path)
    paths = sorted(tmp_path.iterdir())

    with caplog.at_level(logging.DEBUG):
        result = FilterPaths(rule=lambda path: True)(paths)

    assert len(result) == 30
    assert caplog.text.count("(30 items)") >= 2   # the entry record (paths=...) and the result
    assert "f29.txt" not in caplog.text


def test_scanner_actions_return_the_real_unshortened_result(tmp_path):
    """Verify shortening only affects what is logged, never the returned value."""
    _make_files(tmp_path)

    assert [path.name for path in CollectFiles()(tmp_path)] == [f"f{i:02d}.txt" for i in range(30)]
