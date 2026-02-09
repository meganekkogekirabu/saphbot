"""
Replace {{l}} with {{alt}} in alternative forms sections.

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
from typing import Generator

import mwparserfromhell
from lxml import etree  # pyright: ignore
from pywikibot import Page, Site

from lib.multiprocessor import ConcurrentBot

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = Site()


def iter_pages() -> Generator[Page, None, None]:
    iterator = etree.iterparse("dumps/latest.xml", events=("end",), tag=("{*}page"))
    for _, elem in iterator:
        text = elem.find("{*}revision/{*}text").text
        namespace = elem.find("{*}ns").text

        if namespace not in ["0", "118"]:
            continue

        if "Alternative forms" not in text:
            continue

        title = elem.find("{*}title").text

        code = mwparserfromhell.parse(text)
        sections = code.get_sections()

        for section in sections:
            try:
                heading = section.get(0)
            except IndexError:
                continue

            if heading.title != "Alternative forms":
                continue

            templates = section.filter_templates(matches=lambda t: t.name == "l")

            if len(templates) == 0:
                continue

            yield Page(site, title)

            break


def treat(page: Page) -> Page | None:
    code = mwparserfromhell.parse(page.text)
    sections = code.get_sections()

    for section in sections:
        try:
            heading = section.get(0)
        except IndexError:
            continue

        if heading.title != "Alternative forms":
            continue

        templates = section.filter_templates(matches=lambda t: t.name == "l")

        if len(templates) == 0:
            continue

        for template in templates:
            template.name = "alt"

    text = str(code)
    if text != page.text:
        page.text = text
        return page

    return None


concur = ConcurrentBot(
    treat,
    "replace {{[[Template:l|l]]}} with {{[[Template:alt|alt]]}} in alternative forms sections",
    iter_pages(),
)

concur.start()
