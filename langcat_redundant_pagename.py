import pywikibot
from pywikibot.page import BasePage
from pywikibot import pagegenerators
import re
import signal

signal.signal(signal.SIGINT, lambda *_: exit(130))

site = pywikibot.Site()
tl_page = pywikibot.Page(site, "Template:langcat")
gen = BasePage(tl_page).getReferences(only_template_inclusion=True, namespaces=0)

repl = re.compile("{{langcat\\|{{pagename}}}}", flags = re.I)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = repl.sub("{{langcat}}", page.text)
    page.text = page.text.replace("{{langcat|" + page.title() + "}}", "{{langcat}}")
    page.save("Remove redundant pagenames from {{[[Template:langcat|langcat]]}} invocations")