"""
Replace raw topic category links like [[Category:en:Topic]] with {{C}}, like {{C|en|Topic}}.

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
from pywikibot import pagegenerators
from lib.misc import merge_templates

site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Entries with topic categories using raw markup by language"
)
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 118])

is_category = re.compile(r"\[\[cat(?:egory):([^\]]+)\]\]", flags=re.I)

for page in pagegenerators.PreloadingGenerator(gen):
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
    page.save("replace raw topic category markup with {{[[Template:topics|C]]}}")
