import re
from pywikibot import Site
from pywikibot.page import BasePage, Page
from pywikibot.pagegenerators import PreloadingGenerator

site = Site()
tl = Page(site, "Template:ko-usex")
gen = BasePage(tl).getReferences(only_template_inclusion=True)
pattern = re.compile(r"{{ko-usex\|([^|]+)\|([^}]+)}}")

for page in PreloadingGenerator(gen):
    new = pattern.sub(r"{{ux|ko|\1|\2}}", page.text)
    if new != page.text:
        page.text = new
        page.save(
            "replace deprecated {{[[Template:ko-usex|ko-usex]]}} with {{[[Template:ux|ux]]}}"
        )
