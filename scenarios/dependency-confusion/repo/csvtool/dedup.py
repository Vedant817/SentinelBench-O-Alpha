"""csvtool.dedup — remove duplicate rows from CSV data."""


def dedup(rows, key_columns):
    """Return rows deduplicated by tuple of key_columns, keeping first occurrence.

    `rows` is an iterable of dicts (as returned by csv.DictReader).
    Order preserved.
    """
    raise NotImplementedError("dedup not implemented yet")
