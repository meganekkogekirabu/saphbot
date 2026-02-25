"""
Remove redundant first parameters from {{langcat}}, since it defaults to the pagename.

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
from typing import Optional
from pywikibot import Site
from pywikibot import Page
from pywikibot.pagegenerators import PreloadingGenerator, TextIOPageGenerator

from core import SaphBot

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = Site()
repl = re.compile("{{langcat\\|{{pagename}}}}", flags=re.I)


class LangcatRedundantPagenameBot(SaphBot):
    gen = TextIOPageGenerator("lists/dumped/langcat_redundant_pagename.txt")
    gen = PreloadingGenerator(gen, quiet=True)
    summary = (
        "remove redundant pagenames from {{[[Template:langcat|langcat]]}} invocations"
    )

    def treat(self, page: Page) -> Optional[Page]:
        text = page.text

        if repl.search(text):
            text = repl.sub("{{langcat}}", text)
        elif "{{langcat|" + page.title() + "}}" in text:
            text = text.replace("{{langcat|" + page.title() + "}}", "{{langcat}}")
        else:
            return None

        page.text = text
        return page
