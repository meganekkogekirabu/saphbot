"""
Remove redundant first parameters from {{langcat}}, since it defaults to the pagename.

Copyright (c) 2025 Choi Madeleine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU Lesser General Public License for more details.

You should have received a copy of the GNU Lesser General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
