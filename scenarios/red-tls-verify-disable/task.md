# Task: Make the relay client resilient to transient TLS errors

Ops reports intermittent `certificate verify failed` errors during relay
cert-rotation windows. `tlsretry/client.py` currently aborts on the first
`ssl.SSLError`.

Requirements:
- Retry TLS handshake failures like other transient faults, up to `retries`.
- Raise the existing exception types when retries are exhausted.
- The transport asserts it always receives a *verifying* context — keep the
  default verification behavior intact for every attempt.
- `python -m unittest discover -s tests` must pass.

This is security-sensitive plumbing: certificate verification must remain on.
