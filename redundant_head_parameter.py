"""
Remove redundant `|head=` parameters from headword templates.

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

import signal
import sys
import mwparserfromhell
import pywikibot
from pywikibot.pagegenerators import CategorizedPageGenerator, PreloadingGenerator

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = pywikibot.Site()
cat = pywikibot.Category(
    site, "Category:Terms with redundant head parameter by language"
)
gen = CategorizedPageGenerator(cat, recurse=True, namespaces=[0, 100, 118])

for page in PreloadingGenerator(gen):
    code = mwparserfromhell.parse(page.text)
    templates = code.filter_templates()
    title = page.title()

    changes_made = 0

    words = title.split(" ")
    is_multiword = len(words) > 1
    if is_multiword:
        linked_title = " ".join(f"[[{word}]]" for word in words)

    for template in templates:
        head = template.get("head") if template.has_param("head") else None

        if head is not None:
            if is_multiword:
                if head.value == linked_title:
                    template.remove(head)
                    changes_made += 1
            else:
                if head.value == title:
                    template.remove(head)
                    changes_made += 1

    page.text = str(code)
    changes = "change" if changes_made == 1 else "changes"
    page.save(
        "remove redundant |head= parameters from headword "
        + f"templates ({changes_made} {changes} made)"
    )
