"""
Add the `inactive=1` flag to Babel for users whose last contribution was more than 2 years ago.
Discussion: [[Wiktionary:Beer parlour/2025/April#Disabling Babel categorisation for inactive users]]
"""

from datetime import timedelta
import re
import signal
import sys
import pywikibot
from pywikibot.page import BasePage
from pywikibot.pagegenerators import PreloadingGenerator
from pywikibot.exceptions import LockedPageError

signal.signal(signal.SIGINT, lambda *_: sys.exit(0))

ignore = []

with open("lists/babel_cat_ignore.txt", "r", encoding="utf-8") as file:
    for line in file:
        ignore.append(line)

site = pywikibot.Site()
tl_page = pywikibot.Page(site, "Template:Babel")
gen = BasePage(tl_page).getReferences(only_template_inclusion=True, namespaces=2)

exp = re.compile(r"({{babel[^}]+)", flags=re.I)

for page in PreloadingGenerator(gen):
    title = page.title()

    if "/" not in title and title not in ignore and "inactive=1" not in page.text:
        last_edit: tuple | None = pywikibot.User(site, title).last_edit

        if last_edit is None:
            continue

        try:
            delta = (site.server_time() - last_edit[2]) >= timedelta(days=730)

            if delta:
                page.text = exp.sub(r"\1|inactive=1", page.text)
                page.save(
                    "mark users whose last contribution was more than 2 years "
                    + "ago as inactive in Babel",
                )

        except LockedPageError:
            continue
