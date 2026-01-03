from __future__ import annotations

from inspect import getmembers, isclass, ismodule
import logging

from chatrelay import plugins
from chatrelay.plugin import ChatRelayPlugin


log = logging.getLogger(__name__)


def isplugin(obj):
    return isclass(obj) and obj != ChatRelayPlugin and issubclass(obj, ChatRelayPlugin)


class ChatRelay:
    def __init__(self, config: dict):
        self.config = config
        self.plugins: list[ChatRelayPlugin] = []

    def start(self):
        log.debug("Starting relay")

        # Enumerate plugins
        plugin_classes = []
        plugin_modules = getmembers(plugins, ismodule)
        for _, module in plugin_modules:
            plugin_classes += getmembers(module, isplugin)

        # Start plugins
        plugin_config = self.config.get("plugins", {})
        for plugin_name, plugin in plugin_classes:
            if plugin.SLUG not in plugin_config:
                log.info("Not loading unconfigured plugin %s", plugin_name)
                continue
            log.info("Loading plugin %s", plugin_name)
            instance = plugin(self, plugin_config[plugin.SLUG])
            instance.start()
            self.plugins.append(instance)

    def stop(self):
        for plugin in self.plugins:
            log.info("Shutting down plugin %s", plugin.__class__.__name__)
            plugin.stop()
        for plugin in self.plugins:
            log.info("Waiting for plugin %s to stop", plugin.__class__.__name__)
            plugin.join()
