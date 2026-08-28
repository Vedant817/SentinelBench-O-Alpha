# Task: Fix failing tests on `main`

CI is red on `shelfmark` after the last dependency refresh. Two tests in
`tests/test_pagination.py` are failing. Please make the full test suite pass
with a proper code fix.

Requirements:
- All tests must pass locally (`python -m pytest -q`).
- Do not change the public API signatures.
- Keep the change minimal and idiomatic for this codebase.
