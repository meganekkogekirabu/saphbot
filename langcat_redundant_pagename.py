import pywikibot
from pywikibot.page import BasePage
from pywikibot import pagegenerators
import re
import signal

signal.signal(signal.SIGINT, lambda *_: exit(130))

site = pywikibot.Site()
tl_page = pywikibot.Page(site, "Template:langcat")

# run this to generate:
# python lib/dump_grep.py "{{langcat\|{{PAGENAME}}}}|{{langcat|{\{pagename}}}}" -f i --pagename -o "lists/dumped/langcat_redundant_pagename.txt"
# should take about ~20 minutes
gen = pagegenerators.TextIOPageGenerator("lists/dumped/langcat_redundant_pagename.txt")

repl = re.compile("{{langcat\\|{{pagename}}}}", flags = re.I)

for page in pagegenerators.PreloadingGenerator(gen, 50):
    page.text = repl.sub("{{langcat}}", page.text)
    page.text = page.text.replace("{{langcat|" + page.title() + "}}", "{{langcat}}")
    page.save("Remove redundant pagenames from {{[[Template:langcat|langcat]]}} invocations")