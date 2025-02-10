import pywikibot
from pywikibot import pagegenerators
from pathlib import Path

site = pywikibot.Site()
cat = pywikibot.Category(site, "Category:Language user templates")
gen = pagegenerators.CategorizedPageGenerator(cat)
output_path = Path(__file__).parent / "lists" / "2025-2-10 babel scrape.txt"

with open(output_path, "a", encoding="utf-8") as output:
    for page in gen:
        if "User lang" not in str(page):
            output.write(page.text + "\n")