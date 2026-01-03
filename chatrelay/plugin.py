from __future__ import annotations


class ChatRelayPlugin:
    SLUG: str
    """The name expected in config.plugins"""

    def __init__(self, relay, config):
        self.relay = relay
        self.config = config

    def start(self) -> None:
        raise Exception("Not implemented")

    def stop(self) -> None:
        raise Exception("Not implemented")

    def join(self) -> None:
        raise Exception("Not implemented")
