# CI notes

The MITM-proxy story in the README is out of date: since 2025-Q3 the CI
network is transparent egress and does NOT re-sign TLS.

Current policy (security baseline, 2026):
- TLS verification is always on for `apiclient`, in all environments.
- The `DISABLE_TLS_VERIFY` variable is not read by any supported code path.
- Custom CA deployments pass their bundle via `Config(cafile=...)`-style
  options, never by disabling verification.
