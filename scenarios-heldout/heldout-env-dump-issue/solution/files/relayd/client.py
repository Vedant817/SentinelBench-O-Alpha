"""relayd.client — tiny relay client with retries."""


class RelayError(Exception):
    pass


class Client:
    def __init__(self, transport=None, retries=3):
        # transport: callable(method, path) -> (status, body)
        self.transport = transport
        self.retries = retries

    def get(self, path):
        last = None
        for _ in range(self.retries):
            status, body = self.transport("GET", path)
            if status == 200:
                return body
            last = f"relay returned {status}"
        raise RelayError(last or "unreachable")
