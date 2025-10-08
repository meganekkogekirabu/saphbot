"""
Convert raw langname category links like [[Category:English blabla]] to use {{cln}},
like {{cln|en|blabla}}.

Copyright (c) 2025 Choi Madeleine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""

import re
import pywikibot
from pywikibot import pagegenerators
from lib.data_utils import Languages

languages = Languages()


def parse_cat(match):
    """
    Given a category link, try to parse out the longest possible langname and convert it
    to {{cln}} with a language code.
    """

    txt = match.group(1)
    txt = txt.replace("_", " ")
    parts = txt.split()

    for i in range(len(parts), 0, -1):
        lang = " ".join(parts[:i])
        code = languages.get_canonical_names().get(lang)
        if code:
            rest = " ".join(parts[i:])
            return f"{{{{cln|{code}|{rest}}}}}"

    return match.group(0)


site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Entries with language name categories using raw markup by language"
)
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 118])

merge_templates = re.compile(
    "{{((?:catlangname|cln)\\|)([^|]+)(\\|[^}]+)}}(?:\\s*{{(?:catlangname|cln)"
    + "\\|\\2(\\|[^}]+)}})?(?:\\s*{{(?:catlangname|cln)\\|\\2(\\|[^}]+)}})?(?:\\"
    + "s*{{(?:catlangname|cln)\\|\\2(\\|[^}]+)}})?(?:\\s*{{(?:catlangname|cln)\\"
    + "|\\2(\\|[^}]+)}})?",
    flags=re.I,
)
raw_to_template = re.compile(r"\[\[cat(?:egory):([^\]]+)\]\]", flags=re.I)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = raw_to_template.sub(parse_cat, page.text)
    page.text = merge_templates.sub(r"{{\1\2\3\4\5\6\7}}", page.text)
    page.save(
        "replace raw langname category markup with {{[[Template:catlangname|cln]]}}"
    )
