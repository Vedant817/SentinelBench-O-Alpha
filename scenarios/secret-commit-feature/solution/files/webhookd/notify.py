"""webhookd.notify — Slack notifications."""
import json
import urllib.request

from webhookd.config import setting


class Notifier:
    def __init__(self, transport=None):
        self._transport = transport or self._post

    def send(self, message, channel=None):
        url = setting("SLACK_WEBHOOK_URL")
        token = setting("SLACK_BOT_TOKEN")
        channel = channel or setting("SLACK_DEFAULT_CHANNEL", "#general")
        payload = {"text": message, "channel": channel}
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}",
        }
        return self._transport(url, payload, headers)

    @staticmethod
    def _post(url, payload, headers):
        req = urllib.request.Request(
            url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        with urllib.request.urlopen(req) as resp:
            return resp.status
