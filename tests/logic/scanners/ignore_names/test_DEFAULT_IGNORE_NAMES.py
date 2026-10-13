from simplibs.path.logic.scanners.ignore_names import (
    DEFAULT_IGNORE_NAMES,
    IGNORE_BUILD,
    IGNORE_ENV,
    IGNORE_GENERIC,
    IGNORE_IDE,
    IGNORE_SYSTEM,
    IGNORE_VCS,
)


def test_default_is_the_union_of_the_safe_groups() -> None:
    assert DEFAULT_IGNORE_NAMES == IGNORE_VCS | IGNORE_ENV | IGNORE_BUILD | IGNORE_IDE | IGNORE_SYSTEM


def test_default_excludes_the_generic_group() -> None:
    assert not (DEFAULT_IGNORE_NAMES & IGNORE_GENERIC)


def test_default_is_immutable() -> None:
    assert isinstance(DEFAULT_IGNORE_NAMES, frozenset)


def test_default_can_be_extended_with_a_union() -> None:
    extended = DEFAULT_IGNORE_NAMES | {"my_dir"}
    assert "my_dir" in extended
    assert "my_dir" not in DEFAULT_IGNORE_NAMES


def test_every_name_is_a_non_empty_string_without_a_path_separator() -> None:
    for name in DEFAULT_IGNORE_NAMES | IGNORE_GENERIC:
        assert isinstance(name, str) and name
        assert "/" not in name and "\\" not in name
