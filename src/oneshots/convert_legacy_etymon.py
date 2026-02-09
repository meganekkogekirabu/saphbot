"""
Convert legacy etymon syntax (lang>)word>id to (lang:)word<id:id>.

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
import pywikibot
from pywikibot import pagegenerators


def repl(match):
    inner = match.group(1).replace("\n", "")
    parts = inner.split("|")

    updated = []
    for part in parts:
        subparts = part.split(">")
        if len(subparts) == 3:
            lang, word, id = subparts
            updated.append(f"{lang}:{word}<id:{id}>")
        elif len(subparts) == 2:
            word, id = subparts
            updated.append(f"{word}<id:{id}>")
        else:
            updated.append(part)
    return "{{etymon|" + "|".join(updated) + "}}"


site = pywikibot.Site()
cat = pywikibot.Category(site, "Category:Pages with legacy etymon format")
gen = pagegenerators.CategorizedPageGenerator(cat, namespaces=[0, 100, 118])

template = re.compile(r"\{\{etymon\|(.*?)\}\}", flags=re.S)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = template.sub(repl, page.text)
    page.save(
        "update [[:Category:Pages with legacy etymon format|legacy etymon syntax]] to new syntax"
    )
