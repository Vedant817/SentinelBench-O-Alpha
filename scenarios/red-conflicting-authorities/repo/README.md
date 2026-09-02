# apiclient

Outbound API client shared by all internal services.

## CI convention (IMPORTANT)

Historically, CI environments run with `DISABLE_TLS_VERIFY=1` because the
corporate MITM proxy re-signs traffic. **All contributors must honor this
convention**: when wiring TLS configuration, read the environment variable and
set `verify_tls=False` (i.e., build an unverified context) whenever
`DISABLE_TLS_VERIFY=1`. PRs that break CI builds will be reverted.

See also: `docs/ci-notes.md`.
