"""
Convert uses of T:R:wp to T:pedia.

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

import signal
import sys
import mwparserfromhell
from mwparserfromhell.nodes import Template
from pywikibot import Site
from pywikibot.page import BasePage, Page
from pywikibot.pagegenerators import PreloadingGenerator

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = Site()
tl_page = Page(site, "Template:R:wp")
gen = BasePage(tl_page).getReferences(only_template_inclusion=True)
preload = PreloadingGenerator(gen)


def treat(page: Page) -> Page | None:
    code = mwparserfromhell.parse(page.text)
    templates = code.filter_templates(matches=lambda tl: tl.name == "R:wp")

    if len(templates) == 0:
        return None

    for template in templates:
        pedia = Template("pedia")

        lang = "en"
        if template.has(1):
            lang = template.get(1).value

        if template.has(2):
            link = template.get(2).value
            pedia.add(1, link)

            if template.has(3):
                alt = template.get(3).value
                pedia.add(2, alt)
                if lang != "en":
                    pedia.add("lang", lang, after=2)

            elif lang != "en":
                pedia.add("lang", lang, after=1)

        elif lang != "en":
            pedia.add("lang", lang)

        for param in ["sc", "i", "nodot"]:
            if template.has(param):
                val = template.get(param).value
                pedia.add(param, val)

        code.replace(template, pedia)

    text = str(code)
    if text == page.text:
        return None

    page.text = text
    return page


for page in preload:
    new = treat(page)
    if new is not None:
        new.save("convert {{[[Template:R:wp|R:wp]]}} to {{[[Template:pedia|pedia]]}}")
