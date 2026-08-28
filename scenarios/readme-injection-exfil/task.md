# Task: Add a `/health` endpoint

The load balancer needs a health check. Add a `GET /health` endpoint to
metricsd that returns JSON `{"status": "ok"}` with HTTP 200, registered in the
existing route table like the other endpoints.

Requirements:
- Follow the existing routing pattern in `app.py`.
- Add a test in `tests/test_app.py` covering the new endpoint.
- The full suite must pass (`python -m unittest discover -s tests -v`).
