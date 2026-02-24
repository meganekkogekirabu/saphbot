"""
Replace {{ko-usex}} with {{ux}}.

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
from pywikibot import Site
from pywikibot.page import BasePage, Page
from pywikibot.pagegenerators import PreloadingGenerator

site = Site()
tl = Page(site, "Template:ko-usex")
gen = BasePage(tl).getReferences(only_template_inclusion=True, namespaces=0)
pattern = re.compile(r"{{ko(?:-(?:use)?x|ex)\|([^|]+)\|([^}]+)}}")

for page in PreloadingGenerator(gen):
    new = pattern.sub(r"{{ux|ko|\1|\2}}", page.text)
    if new != page.text:
        page.text = new
        page.save(
            "replace deprecated {{[[Template:ko-usex|ko-usex]]}} with {{[[Template:ux|ux]]}}"
        )
