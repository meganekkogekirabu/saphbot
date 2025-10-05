"""
Replace raw topic category links like [[Category:en:Topic]] with {{C}}, like {{C|en|Topic}}.
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
