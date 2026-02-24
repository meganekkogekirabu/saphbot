import re
import signal
import sys
from functools import lru_cache

from pywikibot import Category, Page, Site
from pywikibot.exceptions import InvalidTitleError
from pywikibot.pagegenerators import CategorizedPageGenerator, PreloadingGenerator
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
