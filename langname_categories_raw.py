import re
from data_utils import Languages
import pywikibot
from pywikibot import pagegenerators

languages = Languages()

def parse(match):
    txt = match.group(1)
    txt = txt.replace("_", " ")
    parts = txt.split()
    
    # Try to match the longest possible langname.
    for i in range(len(parts), 0, -1):
        lang = ' '.join(parts[:i])
        code = languages.get_canonical_names().get(lang)
        if code:
            rest = ' '.join(parts[i:])
            return f"{{{{cln|{code}|{rest}}}}}"

    return match.group(0)

def raw_to_template(txt):
    pattern = re.compile(r"\[\[cat(?:egory):([^\]]+)\]\]", flags = re.I)
    return pattern.sub(lambda m: parse(m), txt)

site = pywikibot.Site()
cat = pywikibot.Category(site, "Category:Entries with language name categories using raw markup by language")
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 118])

for page in pagegenerators.PreloadingGenerator(gen, 10):
    merge_templates = re.compile(r"{{((?:catlangname|cln)\|)([^|]+)(\|[^}]+)}}(?:\s*{{(?:catlangname|cln)\|\2(\|[^}]+)}})?(?:\s*{{(?:catlangname|cln)\|\2(\|[^}]+)}})?(?:\s*{{(?:catlangname|cln)\|\2(\|[^}]+)}})?(?:\s*{{(?:catlangname|cln)\|\2(\|[^}]+)}})?", flags = re.I)
    page.text = raw_to_template(page.text)
    page.text = merge_templates.sub(r"{{\1\2\3\4\5\6\7}}", page.text)
    page.save("replace raw langname category markup with {{[[Template:catlangname|cln]]}}")
