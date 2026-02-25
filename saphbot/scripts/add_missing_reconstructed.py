"""
Add {{reconstructed}} to pages in the Reconstruction namespace which are missing it.

Copyright (c) 2025-2026 Choi Madeleine

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

from typing import Optional
import pywikibot
from pywikibot import Page
from pywikibot.pagegenerators import CategorizedPageGenerator, PreloadingGenerator

from core import SaphBot

site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Entries missing Template:reconstructed by language"
)


class AddMissingReconstructedBot(SaphBot):
    gen = CategorizedPageGenerator(cat, recurse=True, namespaces=118)
    gen = PreloadingGenerator(gen, quiet=True)
    summary = "add {{[[Template:reconstructed|reconstructed]]}}"

    def treat(self, page: Page) -> Optional[Page]:
        page.text = "{{reconstruction}}\n" + page.text
        return page
