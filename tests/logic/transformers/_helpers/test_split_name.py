from pathlib import Path
import pytest
from simplibs.path.logic.transformers._helpers import split_name


@pytest.mark.parametrize(
    "path, expected",
    [
        ("report.txt", ("report", ".txt")),
        ("dir/report.txt", ("report", ".txt")),
        ("archive.tar.gz", ("archive", ".tar.gz")),
        ("archive.tar.bz2", ("archive", ".tar.bz2")),
        ("ARCHIVE.TAR.GZ", ("ARCHIVE", ".TAR.GZ")),
        ("my.report.v2.txt", ("my.report.v2", ".txt")),
        ("noext", ("noext", "")),
        (".bashrc", (".bashrc", "")),
        (".tar.gz", (".tar", ".gz")),
        ("data.tar", ("data", ".tar")),
    ],
)
def test_split_name(path, expected) -> None:
    """The name splits into stem and suffix, with `.tar.*` kept together."""
    assert split_name(Path(path)) == expected
