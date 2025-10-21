"""
Convert raw langname category links like [[Category:English blabla]] to use {{cln}},
like {{cln|en|blabla}}.

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

import re
import mwparserfromhell
import pywikibot
from pywikibot import Page
from pywikibot.pagegenerators import PetScanPageGenerator
from lib.data_utils import Languages
from lib.misc import merge_templates

languages = Languages()


def parse_cat(txt: str) -> str:
    """
    Given a category link, try to parse out the longest possible langname and convert it
    to {{cln}} with a language code.
    """

    txt = txt.replace("_", " ")
    parts = txt.split()

    for i in range(len(parts), 0, -1):
        lang = " ".join(parts[:i])
        code = languages.get_canonical_names().get(lang)
        if code:
            rest = " ".join(parts[i:])
            return f"{{{{cln|{code}|{rest}}}}}"

    return txt


is_category = re.compile(r"\[\[cat(?:egory):([^\]]+)\]\]", flags=re.I)


def treat(page: Page) -> Page | None:
    code = mwparserfromhell.parse(page.text)

    # first pass: convert cat links to templates

    links = code.filter_wikilinks(
        matches=lambda link: is_category.search(str(link)) is not None
    )

    for link in links:
        title = str(link.title)[9:]
        parts = title.split(":")

        if len(parts) == 2:
            lang, topic = parts
            code.replace(link, f"{{{{C|{lang}|{topic}}}}}")
        else:
            template = parse_cat(title)
            if template != title:
                code.replace(link, template)

    # second pass: merge cln templates

    cln_templates = code.filter_templates(matches=lambda tl: tl.name == "cln")
    merge_templates(code, cln_templates)

    # third pass: merge c/C/topics templates

    topic_templates = code.filter_templates(
        matches=lambda tl: tl.name in ["topics", "c", "C"]
    )

    merge_templates(code, topic_templates)

    text = str(code)
    if text != page.text:
        page.text = text
        return page

    return None


site = pywikibot.Site()

petscan = PetScanPageGenerator(
    [
        "Entries with language name categories using raw markup by language",
        "Entries with topic categories using raw markup by language",
    ],
    subset_combination=False,
    namespaces=[0, 118],
    extra_options={
        "depth": 1,
    },
)

gen = petscan.query()

for result in gen:
    page = Page(result.title)
    new = treat(page)
    if new is not None:
        new.save("clean up raw category markup")
