from simplibs.path.logic.scanners.ignore_names import IGNORE_IDE


def test_ignore_ide_contents() -> None:
    assert IGNORE_IDE == frozenset({".fleet", ".idea", ".settings", ".vs", ".vscode"})


def test_ignore_ide_is_immutable() -> None:
    assert isinstance(IGNORE_IDE, frozenset)
