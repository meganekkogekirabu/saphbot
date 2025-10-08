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
import pywikibot
from pywikibot import pagegenerators

site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Entries with topic categories using raw markup by language"
)
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 118])

replace_raw = re.compile(
    r"\[\[cat(?:egory)?:([a-zA-Z\-]{2,11}):([^\]]+)\]\]", flags=re.I
)

merge_templates = re.compile(
    "{{((?:c|topics)\\|)([^|]+)(\\|[^}]+)}}(?:\\s*{{(?:c|topics)"
    + "\\|\\2(\\|[^}]+)}})?(?:\\s*{{(?:c|topics)\\|\\2(\\|[^}]+)}}"
    + ")?(?:\\s*{{(?:c|topics)\\|\\2(\\|[^}]+)}})?(?:\\s*{{(?:c|to"
    + "pics)\\|\\2(\\|[^}]+)}})?",
    flags=re.I,
)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = replace_raw.sub(r"{{C|\1|\2}}", page.text)
    page.text = merge_templates.sub(r"{{\1\2\3\4\5\6\7}}", page.text)
    page.save("replace raw topic category markup with {{[[Template:topics|C]]}}")
