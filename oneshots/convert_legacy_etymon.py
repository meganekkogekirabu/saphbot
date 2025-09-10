import re
import pywikibot
from pywikibot import pagegenerators

def repl(match):
    inner = match.group(1)
    parts = inner.split("|")

    transformed = []
    for part in parts:
        subparts = part.split(">")
        if len(subparts) == 3:
            lang, word, someid = subparts
            transformed.append(f"{lang}:{word}<id:{someid}>")
        elif len(subparts) == 2:
            word, someid = subparts
            transformed.append(f"{word}<id:{someid}>")
        else:
            transformed.append(part)
    return "{{etymon|" + "|".join(transformed) + "}}"

site = pywikibot.Site()
cat = pywikibot.Category(site, "Category:Pages with legacy etymon format")
gen = pagegenerators.CategorizedPageGenerator(cat)

template = re.compile(r"\{\{etymon\|(.*?)\}\}")

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = template.sub(repl, page.text)
    page.save("update [[:Category:Pages with legacy etymon format|legacy etymon syntax]] to new syntax")