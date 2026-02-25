"""
Remove redundant `|head=` parameters from headword templates.

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
import signal
import sys
import mwparserfromhell
import pywikibot
from pywikibot.page import Page
from pywikibot.pagegenerators import CategorizedPageGenerator, PreloadingGenerator
from typing import Optional

from core import SaphBot

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Terms with redundant head parameter by language"
)

# ignore titles which contain apostrophes or dashes
# FIXME: hack; should properly update such pages with `|nolink=1`
ignore = re.compile("['\\-]")


class RedundantHeadParameterBot(SaphBot):
    gen = CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 100, 118])
    gen = PreloadingGenerator(gen)
    summary = "remove redundant |head= parameters from headword templates"

    def treat(self, page: Page) -> Optional[Page]:
        title = page.title()

        if ignore.search(title):
            return None

        code = mwparserfromhell.parse(page.text)
        templates = code.filter_templates()

        words = title.split(" ")
        is_multiword = len(words) > 1

        linked_title = None
        if is_multiword:
            linked_title = " ".join(f"[[{word}]]" for word in words)

        for template in templates:
            head = template.get("head") if template.has_param("head") else None

            if head is not None:
                if is_multiword and head.value == linked_title or head.value == title:
                    template.remove(head)

        page.text = str(code)
        return page
