from simplibs.path.logic.scanners.ignore_names import DEFAULT_IGNORE_NAMES, IGNORE_GENERIC


def test_ignore_generic_contents() -> None:
    assert IGNORE_GENERIC == frozenset({"_build", "build", "dist", "env", "out", "site", "target"})


def test_ignore_generic_is_not_part_of_the_default() -> None:
    """Ambiguous names are opt-in."""
    assert IGNORE_GENERIC.isdisjoint(DEFAULT_IGNORE_NAMES)


def test_ignore_generic_is_immutable() -> None:
    assert isinstance(IGNORE_GENERIC, frozenset)
