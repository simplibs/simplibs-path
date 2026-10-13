from pathlib import Path
from simplibs.path.rules import HasSuffix, IsDir, IsFile, IsHidden, IsWithin, NameIs, IsEmptyFile
from simplibs.path.logic.scanners import collect_paths, filter_paths


def test_rules_combine_with_operators_and_describe_readably() -> None:
    rule = IsFile() & HasSuffix(".py") & ~IsHidden()
    assert rule.describe() == "existing file & suffix '.py' & not hidden path"


def test_rules_work_as_a_scanner_include_filter(tmp_path) -> None:
    (tmp_path / "a.py").write_text("x")
    (tmp_path / "b.txt").write_text("x")
    (tmp_path / ".hidden.py").write_text("x")
    (tmp_path / "sub").mkdir()
    (tmp_path / "sub" / "c.py").write_text("x")
    result = collect_paths(tmp_path, include_filter=HasSuffix(".py") & ~IsHidden())
    assert [p.name for p in result] == ["a.py", "c.py"]


def test_rules_work_as_a_scanner_exclude_filter(tmp_path) -> None:
    (tmp_path / "keep.py").write_text("x")
    (tmp_path / "empty.py").write_text("")
    result = collect_paths(tmp_path, exclude_filter=IsEmptyFile())
    assert [p.name for p in result] == ["keep.py"]


def test_rules_work_in_filter_paths(tmp_path) -> None:
    paths = [tmp_path / "a.py", tmp_path / "b.md", tmp_path / "c.py"]
    assert filter_paths(paths, HasSuffix(".py")) == [paths[0], paths[2]]


def test_rules_combine_with_the_lens_rules(tmp_path) -> None:
    from simplibs.rules.predicates.strings import Contains
    (tmp_path / "test_a.py").write_text("x")
    (tmp_path / "app.py").write_text("x")
    result = collect_paths(tmp_path, include_filter=HasSuffix(".py") & NameIs(Contains("test_")))
    assert [p.name for p in result] == ["test_a.py"]


def test_a_scoped_rule_can_gate_a_computed_path(tmp_path) -> None:
    gate = IsWithin(tmp_path)
    assert gate.is_valid(tmp_path / "out" / "a.md") is True
    assert gate.is_valid(tmp_path / ".." / "escape.md") is False


def test_negated_rules_accept_what_the_plain_rule_rejects(tmp_path) -> None:
    assert (~IsDir()).is_valid(tmp_path / "missing") is True
    assert (~IsDir()).is_valid(tmp_path) is False
