"""
Remove redundant first parameters from {{langcat}}, since it defaults to the pagename.
"""

import re
import signal
import sys
import pywikibot
from pywikibot import pagegenerators

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = pywikibot.Site()

# run this to generate list:
# python lib/dump_grep.py "{{langcat\|{{PAGENAME}}}}|{{langcat|{\{pagename}}}}" -f i --pagename -o "lists/dumped/langcat_redundant_pagename.txt"
# should take about ~20 minutes

gen = pagegenerators.TextIOPageGenerator("lists/dumped/langcat_redundant_pagename.txt")

repl = re.compile("{{langcat\\|{{pagename}}}}", flags=re.I)

for page in pagegenerators.PreloadingGenerator(gen):
    if repl.search(page.text) or "{{langcat|" + page.title() + "}}" in page.text:
        page.text = repl.sub("{{langcat}}", page.text)
        page.text = page.text.replace("{{langcat|" + page.title() + "}}", "{{langcat}}")
        page.save(
            "remove redundant pagenames from {{[[Template:langcat|langcat]]}} invocations"
        )
