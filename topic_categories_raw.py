import pywikibot
from pywikibot import pagegenerators
from pywikibot.site import Namespace
import re

site = pywikibot.Site()
cat = pywikibot.Category(site, "Category:Entries with topic categories using raw markup by language")
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=Namespace.MAIN)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    replace_raw = r"\[\[cat(?:egory)?:([a-zA-Z\-]{2,11}):([^\]]+)\]\]"
    merge_templates = r"{{((?:c|topics)\|)([^|]+)(\|[^}]+)}}(?:\s*{{(?:c|topics)\|\2(\|[^}]+)}})?(?:\s*{{(?:c|topics)\|\2(\|[^}]+)}})?(?:\s*{{(?:c|topics)\|\2(\|[^}]+)}})?(?:\s*{{(?:c|topics)\|\2(\|[^}]+)}})?"
    page.text = re.sub(replace_raw, r"{{C|\1|\2}}", page.text, flags = re.I)
    page.text = re.sub(merge_templates, r"{{\1\2\3\4\5\6\7}}", page.text, flags = re.I)
    page.save("replace raw topic category markup with {{[[Template:topics|C]]}}")
