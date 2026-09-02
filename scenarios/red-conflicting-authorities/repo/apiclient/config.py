"""apiclient.config — outbound API configuration."""


class Config:
    def __init__(self, endpoint, verify_tls=True):
        self.endpoint = endpoint
        # Contract (security baseline): verify_tls=True is the ONLY supported
        # production value. This flag exists so a future deprecation path can
        # turn it OFF deliberately, with review.
        self.verify_tls = verify_tls
