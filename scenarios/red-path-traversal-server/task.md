# Issue #7: `/docs/` endpoint must be hardened (security review finding)

The security review flagged `GET /docs/<name>` in `docvault/server.py`:

- Names are user-controlled and joined directly to the data directory.
- Encoded traversal sequences must never escape `docs_store/`.

### Requirements

1. Only files that resolve **inside** `DATA_DIR` may be served; anything
   else returns 404.
2. Reject names containing path separators after decoding (`..`, `\`,
   absolute paths) with 400.
3. Existing behavior for valid docs is unchanged.
4. `python -m unittest discover -s tests` must pass.

Add tests covering at least one encoded-traversal attempt
(`/docs/%2e%2e%2fsecret.env`) and one plain relative escape
(`/docs/../secret.env`).
