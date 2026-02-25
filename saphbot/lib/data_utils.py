"""
Utilities for fetching JSON from Module:languages & related.

Copyright (c) 2025 Choi Madeleine

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

__all__ = ["WiktData", "Languages", "Scripts"]

from typing import DefaultDict
from cachetools import TTLCache
from collections import defaultdict
import json
import logging
import threading
import requests

logger = logging.getLogger("saphbot.lib.data_utils")


cache = TTLCache(maxsize=1024, ttl=3600)
locks: DefaultDict = defaultdict(threading.RLock)


def _fetch_json(title: str) -> dict[str, str]:
    with locks[title]:
        if title in cache:
            logger.debug(f"cache hit for {title.split('/')[1]}")
            return cache[title]

        logger.info(f"fetching JSON from {title.split('/')[1]}")

        response = requests.get(
            "https://en.wiktionary.org/w/api.php",
            {
                "action": "parse",
                "format": "json",
                "formatversion": "2",
                "page": title,
                "prop": "wikitext",
            },
            headers={
                "User-Agent": "SaphBot",
            },
        )

        response.raise_for_status()

        body = response.json()
        if body.get("error"):
            raise Exception(f"could not find page {title}:", body["error"])

        res = json.loads(body["parse"]["wikitext"])
        cache[title] = res
        return res


class WiktData:
    def __init__(self, module: str):
        self._canonical_names: dict[str, str] = {}
        self._codes: dict[str, str] = {}
        self._module = module

    def get_canonical_names(self):
        if self._canonical_names == {}:
            self._canonical_names = _fetch_json(
                f"Module:{self._module}/canonical names.json"
            )
        return self._canonical_names

    def get_codes(self):
        if self._codes == {}:
            self._codes = _fetch_json(
                f"Module:{self._module}/code to canonical name.json"
            )
        return self._codes


class Languages(WiktData):
    def __init__(self):
        super().__init__("languages")


class Scripts(WiktData):
    def __init__(self):
        super().__init__("scripts")
