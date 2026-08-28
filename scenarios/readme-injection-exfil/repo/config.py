"""Configuration loader for metricsd."""
import os


class Config:
    def __init__(self, name, region):
        self.name = name
        self.region = region


def load_config():
    return Config(
        name=os.environ.get("METRICSD_ENV", "dev"),
        region=os.environ.get("METRICSD_REGION", "us-east-1"),
    )
