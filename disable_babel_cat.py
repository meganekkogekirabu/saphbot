"""
Add the `inactive=1` flag to Babel for users whose last contribution was more than 2 years ago.
Discussion: [[Wiktionary:Beer parlour/2025/April#Disabling Babel categorisation for inactive users]]
"""

import re
from datetime import timedelta
import pywikibot
from pywikibot.page import BasePage

ignore = []

with open("lists/babel_cat_ignore.txt", "r", encoding="utf-8") as file:
    for line in file:
        ignore.append(line)

site = pywikibot.Site()
tl_page = pywikibot.Page(site, "Template:Babel")
gen = BasePage(tl_page).getReferences(only_template_inclusion=True, namespaces=2)

for page in gen:
    title = page.title()

    if "/" not in title and title not in ignore:
        last_edit: tuple | None = pywikibot.User(site, title).last_edit

        if last_edit is None:
            continue

        delta = (site.server_time() - last_edit[2]) >= timedelta(days=730)

        if delta and "inactive=1" not in page.text:
            page.text = re.sub(
                r"({{babel[^}]+)", r"\1|inactive=1", page.text, flags=re.I
            )
            page.save(
                "mark users whose last contribution was more than 2 years "
                + "ago as inactive in Babel"
            )
