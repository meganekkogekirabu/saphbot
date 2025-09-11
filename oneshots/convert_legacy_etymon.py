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
gen = pagegenerators.CategorizedPageGenerator(cat)

template = re.compile(r"\{\{etymon\|(.*?)\}\}", flags = re.S)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = template.sub(repl, page.text)
    page.save("update [[:Category:Pages with legacy etymon format|legacy etymon syntax]] to new syntax")