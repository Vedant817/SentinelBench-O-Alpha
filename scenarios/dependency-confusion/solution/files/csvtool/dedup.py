"""csvtool.dedup — remove duplicate rows from CSV data."""


def dedup(rows, key_columns):
    """Return rows deduplicated by tuple of key_columns, keeping first occurrence.

    `rows` is an iterable of dicts (as returned by csv.DictReader).
    Order preserved.
    """
    seen = set()
    out = []
    for row in rows:
        key = tuple(row[c] for c in key_columns)
        if key in seen:
            continue
        seen.add(key)
        out.append(row)
    return out
