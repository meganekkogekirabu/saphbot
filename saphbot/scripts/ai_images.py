#!/usr/bin/env python3

"""
Find pages using AI images.

Copyright (c) 2026 Choi Madeleine

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

from functools import lru_cache
from pywikibot import Category, Page, Site
from pywikibot.exceptions import InvalidTitleError
from pywikibot.pagegenerators import CategorizedPageGenerator, PreloadingGenerator
import re
import signal
import sys
from tqdm import tqdm

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

image_link = re.compile(r"\[\[(?:image|file):([^|\]]+)", flags=re.I)

site = Site()
commons = Site("commons:commons")
category = Category(site, "English lemmas")
gen = CategorizedPageGenerator(category)


@lru_cache(maxsize=100_000)
def is_ai_image(page: Page) -> bool:
    for category in page.categories():
        # dumb heuristic: traversing all the parents to figure out if it's in a
        # subcat of `CAT:AI-generated images` would be super expensive, so just
        # check if "AI-generated" is in the category name
        if "AI-generated" in category.title():
            return True

    return False


def treat(page: Page):
    links = image_link.findall(page.text)

    if len(links) == 0:
        return

    for link in links:
        image = Page(commons, title=link)
        try:
            if is_ai_image(image):
                tqdm.write(
                    f"\033[1;31mAI:\033[0m [[{page.title()}]] [[{image.title()}]]"
                )
                break
        except InvalidTitleError as e:
            print(e)
            continue


preload = PreloadingGenerator(gen, 500, quiet=True)


for page in tqdm(preload, unit="ppg"):
    treat(page)
