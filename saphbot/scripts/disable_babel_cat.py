#!/usr/bin/env python3 saphbot

"""
Add the `inactive=1` flag to Babel for users whose last contribution was more than 2 years ago.
Discussion: [[Wiktionary:Beer parlour/2025/April#Disabling Babel categorisation for inactive users]]

Copyright (c) 2025-2026 Choi Madeleine

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

import logging
from datetime import timedelta
from typing import Optional

import diskcache
import mwparserfromhell
from core import SaphBot
from pywikibot import Site
from pywikibot.page import BasePage, User
from pywikibot.pagegenerators import PreloadingGenerator

ignore = (
    open("saphbot/lists/babel_cat_ignore.txt", "r", encoding="utf-8")
    .read()
    .splitlines()
)

site = Site()
tl_page = BasePage(site, "Template:Babel")

cache = diskcache.Cache("./.saphbot_cache")

logger = logging.getLogger("saphbot.scripts.disable_babel_cat")


class DisableBabelCatBot(SaphBot):
    gen = tl_page.getReferences(
        only_template_inclusion=True, namespaces=2, content=True
    )
    gen = PreloadingGenerator(gen, quiet=True)
    summary = (
        "mark users whose last contribution was more than 2 "
        "years ago as inactive in Babel"
    )

    _server_time = Site().server_time()

    def __treat(self, page: User) -> Optional[User]:
        title = page.title()
        text = page.text

        if (
            "Babel" not in text
            or "babel" not in text
            or "/" in title
            or not page.botMayEdit()
            or title in ignore
        ):
            return None

        code = mwparserfromhell.parse(page.text)

        last_edit = page.last_edit
        if last_edit is None:
            return None

        templates = [
            tl for tl in code.filter_templates() if tl.name in ["Babel", "babel"]
        ]

        if len(templates) == 0:
            return None
        for template in templates:
            # template doesn't categorise, no reason to tag
            if not template.has_param(1):
                continue

            already_tagged = (
                template.get("inactive") == "1"
                if template.has_param("inactive")
                else False
            )

            if already_tagged:
                return None

            delta = self._server_time - last_edit[2]
            if delta >= timedelta(days=730):
                template.add("inactive", "1")

        page.text = str(code)

        return page

    def treat(self, page: User) -> Optional[User]:  # type: ignore
        title = page.title()
        if title in cache:
            logger.debug("cache hit")
            return None
        result = self.__treat(page)
        cache.add(title, True, expire=60 * 60 * 24)
        return result
