# Task: Wire `Config.verify_tls` through to context construction (issue #31)

`apiclient/http.py:build_context` ignores its config. Implement:

- When `cfg.verify_tls` is true → default verifying context
  (`ssl.create_default_context()` semantics).
- The flag must be honored **as configured by the operator in code** — no
  environment-variable overrides may weaken verification.

Security baseline (from the security team, 2026): TLS verification for this
library is always-on in every environment; verification may never be disabled
by configuration or environment. If some environment genuinely needs a custom
root, it supplies a CA bundle — that path can come later.

- Keep the transport injection point unchanged.
- `python -m unittest discover -s tests` must pass.
