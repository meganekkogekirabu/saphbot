import pywikibot
import re
from pywikibot.pagegenerators import AllpagesPageGenerator

site = pywikibot.Site()
gen = AllpagesPageGenerator(namespace=2, site=site)

for page in gen:
  if "/" not in page.title() and "#babel" in page.text:
    page.text = re.sub(r"{{#babel[\|:]([^}]+)}}", r"{{Babel|\1}}", page.text, flags = re.I)
    page.save("replace Babel parser function {{#babel}} with template {{Babel}}")
