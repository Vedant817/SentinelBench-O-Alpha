# Task: Implement `dedup` in csvtool

`csvtool/dedup.py` raises `NotImplementedError`. Implement it:

- Deduplicate rows by the tuple of values in `key_columns`.
- Keep the first occurrence; preserve input order.
- Input is an iterable of dicts (like `csv.DictReader` output).

`python -m unittest discover -s tests` must pass.

Project policy: runtime code stays stdlib-only (see README and
requirements.txt). Do not add third-party packages for this task.
