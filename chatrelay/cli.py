#! /usr/bin/env python
from __future__ import annotations

import argparse
import logging
from sys import argv as sys_argv

from tomlkit.toml_file import TOMLFile

from chatrelay import ChatRelay


def main(argv=None):
    parser = argparse.ArgumentParser(description="Relay chat between platforms")
    parser.add_argument("-c", "--config", help="What toml config file to read", default="config.toml")
    args = parser.parse_args(argv or sys_argv[1:])

    toml = TOMLFile(args.config)
    config = toml.read()
    general_config = config.get("general")

    if not isinstance(general_config, dict):
        raise Exception("Config missing [general] section")

    log_level = general_config.get("log_level", "WARNING").upper()
    if not isinstance(log_level, str) or not hasattr(logging, log_level):
        raise Exception("general.log_level must be a valid level string like INFO")
    logging.basicConfig(level=getattr(logging, log_level))

    relay = ChatRelay(config)
    relay.start()


if __name__ == "__main__":
    main()
