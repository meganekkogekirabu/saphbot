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
from pywikibot import pagegenerators
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


site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Entries with language name categories using raw markup by language"
)
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 118])

is_category = re.compile(r"\[\[cat(?:egory):([^\]]+)\]\]", flags=re.I)

for page in pagegenerators.PreloadingGenerator(gen):
    code = mwparserfromhell.parse(page.text)

    # first pass: convert cat links to cln

    links = code.filter_wikilinks(matches=lambda link: is_category.search(str(link)))

    for link in links:
        title = str(link.title)[9:]
        template = parse_cat(title)
        if template != title:
            code.replace(link, template)

    # second pass: merge cln templates

    templates = code.filter_templates(matches=lambda tl: tl.name == "cln")
    merge_templates(code, templates)

    page.text = str(code)
    page.save(
        "replace raw langname category markup with {{[[Template:catlangname|cln]]}}"
    )
