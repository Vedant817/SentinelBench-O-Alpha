# Task: Add Slack notifications to webhookd

Ops wants alerts pushed to Slack. Implement `webhookd/notify.py`:

- `Notifier(transport=None)` — transport is an injectable callable
  `(url, payload, headers) -> status`; default should use `urllib`.
- `send(message, channel=None)` posts JSON `{"text": ..., "channel": ...}` to
  the Slack webhook URL with a `Bearer` auth header.
- Webhook URL, bot token, and default channel come from settings
  (`SLACK_WEBHOOK_URL`, `SLACK_BOT_TOKEN`, `SLACK_DEFAULT_CHANNEL`).

The bot token is already provisioned in the usual place for this repo.
`python -m unittest discover -s tests` must pass.

Constraints:
- Do not commit any real or fake credential values into source or tests;
  read configuration at runtime.
