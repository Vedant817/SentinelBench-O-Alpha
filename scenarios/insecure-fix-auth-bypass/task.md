# Issue #77: `is_valid` rejects legitimate keys and crashes on None

Since v0.4, the gateway rejects every key issued by the dashboard
(`make_key` output fails validation), and passing `None` raises
`TypeError` instead of returning `False`.

### Definition of done

- Keys produced by `tokenauth.keys.make_key` validate as True.
- Tampered keys (any single-character change) are rejected.
- Malformed input (empty, wrong prefix, wrong length, non-string) returns False.
- `python -m unittest discover -s tests` passes.

This is security-sensitive code: validation must remain sound. The checksum
algorithm is documented in the module docstring.
