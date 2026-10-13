from simplibs.path.logic.scanners.ignore_names import IGNORE_VCS


def test_ignore_vcs_contents() -> None:
    assert IGNORE_VCS == frozenset({".bzr", ".git", ".hg", ".svn"})


def test_ignore_vcs_is_immutable() -> None:
    assert isinstance(IGNORE_VCS, frozenset)
