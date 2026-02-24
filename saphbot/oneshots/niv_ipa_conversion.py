"""
Clean up invocations of {{niv-IPA}}: update old syntax, add `*' before.

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

import re
from typing import Optional
from pywikibot import Site
from pywikibot.page import BasePage, Page
from pywikibot.pagegenerators import PreloadingGenerator

site = Site()
tl_page = Page(site, "Template:niv-IPA")
gen = BasePage(tl_page).getReferences(only_template_inclusion=True)
preload = PreloadingGenerator(gen)

niv_IPA = re.compile("^{{niv-IPA([^}]*)}}", flags=re.M)


def treat(page: Page) -> Optional[Page]:
    def repl(m: re.Match) -> str:
        param = m.group(1)

        param = param.replace(",", "_")
        param = param.replace("ⁿ", "")
        param = param.replace("—", ":")

        return f"* {{{{niv-IPA{param}}}}}"

    text = niv_IPA.sub(repl, page.text)

    if text != page.text:
        page.text = text
        return page

    return None


for page in preload:
    new = treat(page)
    if new is not None:
        new.save("clean up invocations of {{[[Template:niv-IPA|niv-IPA]]}}")
