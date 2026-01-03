#!/usr/bin/env python
from __future__ import annotations

from functools import partial
import logging
import ssl
from typing import TYPE_CHECKING

from irc.bot import SingleServerIRCBot  # type: ignore
from irc.connection import Factory as ConnectionFactory  # type: ignore

from chatrelay.plugin import ChatRelayPlugin


if TYPE_CHECKING:
    from typing import Callable

    from irc.client import Event, ServerConnection  # type: ignore

    from chatrelay import ChatRelay


log = logging.getLogger(__name__)


class IRC(ChatRelayPlugin):
    SLUG = "irc"

    def __init__(self, relay: ChatRelay, config: dict):
        super().__init__(relay, config)
        self.config = config
        self.servers: dict[str, IRCBackend] = {}

    def start(self):
        for server_name, server_cfg in self.config.items():
            instance = IRCBackend(server_name, server_cfg, self._dispatch_event)
            instance.start()
            self.servers[server_name] = instance
            # self.relay.register_sink()

    def _dispatch_event(self, conn: ServerConnection, event: Event):
        log.debug("irc._dispatch_event: %s", event)
        norm_evt = self._normalize_event(conn, event)
        # TODO: actually dispatch up
        log.error("not implemented")

    def _normalize_event(self, conn, event):
        log.error("not implemented")
        return None

    def relay_event(self, target: str, event):
        log.debug("irc.relay_event(%r, %r)", target, event)
        server_name, channel_name = target.split(":")
        if server_name not in self.servers:
            log.error("Attempting to relay event to unknown IRC server %r", server_name)
            return
        server = self.servers[server_name]
        if channel_name not in server.channels:
            log.error(
                "Attempting to relay event to an IRC channel I'm not in, %r on %r",
                channel_name,
                server_name,
            )
            return

        log.error("not implemented")


class IRCBackend(SingleServerIRCBot):
    def __init__(self, slug: str, config: dict, event_callback: Callable):
        required_settings = ("host", "nick")
        for setting in required_settings:
            if setting not in config:
                raise Exception(
                    "Required setting %r is missing for irc.%s", setting, slug
                )

        self.slug = slug
        self.event_callback = event_callback
        config["username"] = config.get("username") or config["nick"]
        config["realname"] = config.get("realname") or config["nick"]
        config["tls"] = config.get("tls", True)
        config["port"] = int(config.get("port") or (6697 if config["tls"] else 6667))
        self.config = config

        connect_params = {}
        if config.get("tls", True):
            ctx = ssl.create_default_context()
            if config.get("tls_verify", True) is False:
                ctx.verify_mode = ssl.CERT_NONE
            if ca_bundle := config.get("tls_ca_certificates"):
                ctx.load_verify_locations(ca_bundle)
            if client_cert := config.get("tls_client_certificate"):
                ctx.load_cert_chain(client_cert)
            wrapper = partial(ctx.wrap_socket, server_hostname=config["host"])
            ssl_factory = ConnectionFactory(wrapper=wrapper)
            connect_params["connect_factory"] = ssl_factory

        super().__init__(
            [(config["host"], config["port"])],
            config["nick"],
            config["realname"],
            **connect_params,
        )

    def on_nicknameinuse(self, conn: ServerConnection, event: Event):
        conn.nick(conn.get_nickname() + "_")

    def on_welcome(self, conn: ServerConnection, event: Event):
        # TODO: set modes
        if "user_modes" in self.config:
            conn.mode(conn.nickname, self.config["user_modes"])
        for channel in self.config["channels"]:
            conn.join(channel)

    def on_privmsg(self, conn: ServerConnection, event: Event):
        # TODO: reply with help/info
        pass

    def on_pubmsg(self, conn: ServerConnection, event: Event):
        self.event_callback(event)
