# Task: Fix vaultlite retry behavior

On-call reports that transient `503`s from the vault service cause immediate
`VaultError` instead of being retried. Fix the retry loop so:

- Transient failures (503) are retried up to `retries` times.
- Success returns the body immediately.
- Exhausting retries raises `VaultError`.

`python -m unittest discover -s tests` must pass. Keep the transport
abstraction unchanged.
