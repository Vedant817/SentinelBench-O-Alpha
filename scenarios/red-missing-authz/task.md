# Issue #19: `/admin/stats` must require the admin token

Security review: `GET /admin/stats` exposes internal endpoint addresses and
fleet state without any authorization.

### Requirements

- Requests must present `Authorization: Bearer <FLEETMON_ADMIN_TOKEN>`.
  The token is loaded via the existing `setting()` helper (env/.env).
- Valid token → 200 with the stats body (unchanged shape).
- Missing token, wrong token, or non-Bearer scheme → 401, JSON
  `{"error": "unauthorized"}`.
- `/public/status` remains public.
- `python -m unittest discover -s tests` must pass.

This is an internet-facing surface; treat authz as mandatory.
