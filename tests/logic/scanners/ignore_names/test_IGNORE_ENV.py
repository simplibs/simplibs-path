from simplibs.path.logic.scanners.ignore_names import IGNORE_ENV


def test_ignore_env_contains_environments_and_dependencies() -> None:
    for name in (".venv", "venv", ".virtualenv", ".poetry", "node_modules", "__pypackages__", ".direnv"):
        assert name in IGNORE_ENV


def test_ignore_env_contains_the_dotenv_secrets_file() -> None:
    assert ".env" in IGNORE_ENV


def test_ignore_env_no_longer_hides_the_ambiguous_env_name() -> None:
    """`env` moved to IGNORE_GENERIC — too common as an ordinary folder name."""
    assert "env" not in IGNORE_ENV


def test_ignore_env_is_immutable() -> None:
    assert isinstance(IGNORE_ENV, frozenset)
