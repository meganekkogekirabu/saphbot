"""
Remove {{#babel}} parser function and replace with {{Babel}}.
Discussion: [[User talk:Saph/2025#About inactive Babel categories]]

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

import pywikibot
import re
from pywikibot.pagegenerators import AllpagesPageGenerator

site = pywikibot.Site()
# if run again, convert to use TextIOPageGenerator w/ a list generated from dump
gen = AllpagesPageGenerator(namespace=2, site=site)

for page in gen:
    if "/" not in page.title() and "#babel" in page.text:
        page.text = re.sub(
            r"{{#babel[\|:]([^}]+)}}", r"{{Babel|\1}}", page.text, flags=re.I
        )
        page.save("replace Babel parser function {{#babel}} with template {{Babel}}")
