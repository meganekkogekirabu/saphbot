"""
Add {{reconstructed}} to pages in the Reconstruction namespace which are missing it.

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

import pywikibot
from pywikibot import pagegenerators

site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Entries missing Template:reconstructed by language"
)
gen = pagegenerators.CategorizedPageGenerator(cat, recurse=True, namespaces=118)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    page.text = "{{reconstructed}}\n" + page.text
    page.save("add {{[[Template:reconstructed|reconstructed]]}}")
