import pywikibot
from pywikibot import pagegenerators

site = pywikibot.Site()
cat = pywikibot.Category(site, "Category:Entries missing Template:reconstructed by language")
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=118)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = "{{reconstructed}}\n" + page.text
    page.save("add {{reconstructed}}")