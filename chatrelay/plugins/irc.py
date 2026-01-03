#!/usr/bin/env python
from __future__ import annotations

import logging

from irc.bot import SingleServerIRCBot  # type: ignore
import irc.strings  # type: ignore

from chatrelay.plugin import ChatRelayPlugin


log = logging.getLogger(__name__)


class IRC(ChatRelayPlugin):
    SLUG = "irc"

    def __init__(self, relay, config):
        super().__init__(relay, config)
        self.config = config
        self.servers: dict[str, IRCBackend] = {}

    def start(self):
        for server_name, server_cfg in self.config.items():
            instance = IRCBackend(**server_cfg)
            self.servers[server_name] = instance
            self.relay.register_sink()

class IRCBackend(SingleServerIRCBot):
    def __init__(self, channel, nickname, server, port=6667):
        log.info("IRC Initialized")
        SingleServerIRCBot.__init__(self, [(server, port)], nickname, nickname)
        self.channel = channel

    def on_nicknameinuse(self, conn, event):
        conn.nick(conn.get_nickname() + "_")

    def on_welcome(self, conn, event):
        conn.join(self.channel)

    def on_privmsg(self, conn, event):
        self.do_command(event, event.arguments[0])

    def on_pubmsg(self, conn, event):
        a = event.arguments[0].split(":", 1)
        if len(a) > 1 and irc.strings.lower(a[0]) == irc.strings.lower(
            self.connection.get_nickname()
        ):
            self.do_command(event, a[1].strip())
        return

    def do_command(self, e, cmd):
        nick = e.source.nick
        c = self.connection

        if cmd == "disconnect":
            self.disconnect()
        elif cmd == "die":
            self.die()
        elif cmd == "stats":
            for chname, chobj in self.channels.items():
                c.notice(nick, "--- Channel statistics ---")
                c.notice(nick, "Channel: " + chname)
                users = sorted(chobj.users())
                c.notice(nick, "Users: " + ", ".join(users))
                opers = sorted(chobj.opers())
                c.notice(nick, "Opers: " + ", ".join(opers))
                voiced = sorted(chobj.voiced())
                c.notice(nick, "Voiced: " + ", ".join(voiced))
        else:
            c.notice(nick, "Not understood: " + cmd)
