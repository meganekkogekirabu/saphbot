#!/usr/bin/env python3 saphbot -n

"""
Replace raw topic category links like [[Category:en:Topic]] with {{C}}, like {{C|en|Topic}}.

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

import re
import mwparserfromhell
from pywikibot import Site
from pywikibot.page import Category, Page
from pywikibot.pagegenerators import CategorizedPageGenerator, PreloadingGenerator
from typing import Optional

from core import SaphBot
from lib.misc import merge_templates

site = Site()
cat = Category(
    site, "Category:Entries with topic categories using raw markup by language"
)

is_category = re.compile(r"\[\[cat(?:egory):([^\]]+)\]\]", flags=re.I)


class TopicCategoriesRawBot(SaphBot):
    gen = CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 118])
    gen = PreloadingGenerator(gen)
    summary = "replace raw topic category markup with {{[[Template:topics|C]]}}"

    def treat(self, page: Page) -> Optional[Page]:
        code = mwparserfromhell.parse(page.text)

        # first pass: convert cat links to templates

        links = code.filter_wikilinks(
            matches=lambda link: is_category.search(str(link)) is not None
        )

        for link in links:
            title = str(link.title)
            parts = title.split(":")

            if len(parts) != 3:
                continue

            lang, topic = title.split(":")[1:]
            code.replace(link, f"{{{{C|{lang}|{topic}}}}}")

        # second pass: merge c/C/topics templates

        templates = code.filter_templates(
            matches=lambda tl: tl.name in ["topics", "c", "C"]
        )

        merge_templates(code, templates)

        page.text = str(code)
        return page
