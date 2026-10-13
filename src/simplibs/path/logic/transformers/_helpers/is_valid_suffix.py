def is_valid_suffix(suffix: str) -> bool:
    """Check whether a string has the shape of a file suffix.

    Args:
        suffix: The candidate suffix.

    Returns:
        True for an empty string (meaning "no suffix") or a string such as
        `.txt` / `.tar.gz` — a dot followed by at least one character and no
        path separator or null byte. False otherwise.
    """

    # 1. An empty suffix means "no suffix" — valid
    if suffix == "":
        return True

    # 2. Otherwise: a dot plus at least one character, without separators or null bytes
    return (
        len(suffix) > 1
        and suffix.startswith(".")
        and not any(char in suffix for char in ("/", "\\", "\0"))
    )


_DESIGN_NOTES = """
# is_valid_suffix — One Definition of "a Suffix"

## Purpose
`change_suffix` (a suffix to put on a path) and the `HasSuffix` rule (a
suffix to look for) must agree on what a suffix is. The shape check used to
live inline in `change_suffix`; it moved here so both share one definition
and cannot drift apart.

## Not an Extension Registry
Any dot-prefixed text is accepted (`.tar.gz`, `.v2`). Whether it is a
*real* extension is not this function's business.
"""
