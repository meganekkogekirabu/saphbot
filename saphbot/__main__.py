"""
Main entry point for running scripts from the command line.

Copyright (c) 2026 Choi Madeleine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import argparse
import colorlog
import importlib
import logging
import signal
import sys

from core import SaphBot, SaphBotOptions

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))
logger = logging.getLogger("saphbot")


def get_arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="saphbot")
    parser.add_argument("module", help="The module to run")
    parser.add_argument("--dry-run", action="store_true", help="Run without saving")
    parser.add_argument(
        "-r",
        "--review",
        action="store_true",
        help="Review diffs before saving each page",
    )
    parser.add_argument(
        "-v", "--verbose", action="store_true", help="Enable debug logging"
    )
    parser.add_argument(
        "-n",
        "--normalise",
        action="store_true",
        help="Run normalisation per [[WT:NORM]] before saving",
    )
    return parser.parse_args()


def setup_logger(verbose: bool):
    formatter = colorlog.ColoredFormatter(
        fmt=(
            "%(log_color)s"
            "%(asctime)s.%(msecs)03d "
            "%(bold)s%(levelname)-8s%(reset)s"
            "%(bold)s%(name)s%(reset)s (%(threadName)s): "
            "%(message)s"
        ),
        datefmt="%H:%M:%S",
    )

    handler = colorlog.StreamHandler()
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG if verbose else logging.INFO)


def normalise_module_name(module_name: str) -> str:
    if "/" not in module_name:
        return module_name
    else:
        # Running directly as e.g. saphbot/scripts/[...].py
        return module_name.split("/")[-1][:-3]


def main():
    args = get_arguments()
    setup_logger(verbose=args.verbose)

    module = normalise_module_name(args.module)
    importlib.import_module(f"scripts.{module}")

    ModuleBot = SaphBot.get_entry()
    logger.debug(f"found entry point: {ModuleBot.__name__}")

    options = SaphBotOptions(dry_run=args.dry_run, normalise=args.normalise)

    ModuleBot(options)._start()


if __name__ == "__main__":
    main()
