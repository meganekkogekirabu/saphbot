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

import requests
import json


def json_from_wikitext(title: str) -> dict:
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

    if response.status_code != 200:
        raise Exception(f"API returned status code {response.status_code}")
        return {}

    body = response.json()
    if body.get("error"):
        raise Exception(f"Could not find page {title}:", body["error"])
        return {}

    return json.loads(body["parse"]["wikitext"])


class WiktData:
    def __init__(self, module: str):
        self.canonical_names: dict[str, str] = {}
        self.language_codes: dict[str, str] = {}
        self.module = module

    def get_canonical_names(self):
        if self.canonical_names == {}:
            self.canonical_names = json_from_wikitext(
                f"Module:{self.module}/canonical names.json"
            )
        return self.canonical_names

    def get_codes(self):
        if self.language_codes == {}:
            self.language_codes = json_from_wikitext(
                f"Module:{self.module}/code to canonical name.json"
            )
        return self.language_codes


class Languages(WiktData):
    def __init__(self):
        super().__init__("languages")


class Scripts(WiktData):
    def __init__(self):
        super().__init__("scripts")
