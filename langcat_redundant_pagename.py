import pywikibot
from pywikibot import pagegenerators
import re
import signal
from tqdm import tqdm

signal.signal(signal.SIGINT, lambda *_: exit(130))

site = pywikibot.Site()

# run this to generate:
# python lib/dump_grep.py "{{langcat\|{{PAGENAME}}}}|{{langcat|{\{pagename}}}}" -f i --pagename -o "lists/dumped/langcat_redundant_pagename.txt"
# should take about ~20 minutes
gen = pagegenerators.TextIOPageGenerator("lists/dumped/langcat_redundant_pagename.txt")
iterator = tqdm(pagegenerators.PreloadingGenerator(gen, 100, quiet = True), unit = "ppg", desc = "Reading", dynamic_ncols = True)

repl = re.compile("{{langcat\\|{{pagename}}}}", flags = re.I)

for page in iterator:
    if repl.search(page.text) or "{{langcat|" + page.title() + "}}" in page.text:
        page.text = repl.sub("{{langcat}}", page.text)
        page.text = page.text.replace("{{langcat|" + page.title() + "}}", "{{langcat}}")
        page.save("Remove redundant pagenames from {{[[Template:langcat|langcat]]}} invocations", quiet = True)
