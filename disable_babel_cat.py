"""
Add the `inactive=1` flag to Babel for users whose last contribution was more than 2 years ago.
Discussion: [[Wiktionary:Beer parlour/2025/April#Disabling Babel categorisation for inactive users]]

Copyright (c) 2025 Choi Madeleine

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
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
