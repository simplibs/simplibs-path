from pathlib import Path


def split_name(path: Path) -> tuple[str, str]:
    """Split a path's final name into a base name and its (extension) suffix.

    Args:
        path: The path whose final name is split.

    Returns:
        `(stem, suffix)`. The suffix is the last extension (`".txt"`), except
        for compound tar archives, where it is the whole `".tar.gz"`.
        `("report", ".txt")`, `("archive", ".tar.gz")`, `(".bashrc", "")`.
    """

    # 1. Plain split — the last extension only
    stem = path.stem
    suffix = path.suffix

    # 2. Compound tar archives keep ".tar" together with the compression suffix
    if suffix and len(stem) > 4 and stem.lower().endswith(".tar"):
        return stem[:-4], stem[-4:] + suffix

    # 3. Everything else
    return stem, suffix


_DESIGN_NOTES = """
# split_name — Name/Suffix Split for Numbered Variants

## Purpose
`make_unique_path` inserts " (1)" between the base name and the extension.
With pathlib's plain `stem`/`suffix`, `archive.tar.gz` would become
`archive.tar (1).gz` — a name whose "real" extension is lost. Treating
`.tar.<compression>` as one suffix yields `archive (1).tar.gz`.

## Why Only `.tar` Is Special
Other multi-dot names (`report.v2.final.txt`) cannot be told apart from a
base name that simply contains dots, so they keep the last extension only:
`report.v2.final (1).txt`. The result is still correct and still opens with
the right program — only `.tar.*` is common enough to deserve a rule.

## Hidden Files
`.bashrc` has no suffix in pathlib's view (its whole name is the stem), so
the number goes at the end: `.bashrc (1)`.
"""
