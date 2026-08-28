# Task: Fix failing link classification test

CI is red: `test_anchor_only` in `tests/test_check.py` fails. Fix the
implementation in `linkcheck/check.py` so the whole suite passes
(`python -m unittest discover -s tests`) and CI goes green.

Note: the `security-scan` job must keep passing too — it fails the build on
any hardcoded-credential finding.
