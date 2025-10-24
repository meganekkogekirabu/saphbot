import signal
import sys
from typing import Generator
from lxml import etree  # pyright: ignore
import mwparserfromhell
from pywikibot import Page, Site
from pywikibot.pagegenerators import PreloadingGenerator
from lib.multiprocessor import ConcurrentBot

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

site = Site()


def iter_pages() -> Generator[Page, None, None]:
    iterator = etree.iterparse("dumps/latest.xml", events=("end",), tag=("{*}page"))
    for _, elem in iterator:
        title = elem.find("{*}title").text
        text = elem.find("{*}revision/{*}text").text
        namespace = elem.find("{*}ns").text

        if namespace not in ["0", "118"]:
            continue

        if "Alternative forms" not in text:
            continue

        code = mwparserfromhell.parse(text)
        sections = code.get_sections()

        for section in sections:
            try:
                heading = section.get(0)
            except IndexError:
                continue

            if heading.title != "Alternative forms":
                continue

            templates = section.filter_templates(matches=lambda t: t.name == "l")

            if len(templates) == 0:
                continue

            yield Page(site, title)

            break


def treat(page: Page) -> Page | None:
    code = mwparserfromhell.parse(page.text)
    sections = code.get_sections()

    for section in sections:
        try:
            heading = section.get(0)
        except IndexError:
            continue

        if heading.title != "Alternative forms":
            continue

        templates = section.filter_templates(matches=lambda t: t.name == "l")

        if len(templates) == 0:
            continue

        for template in templates:
            template.name = "alt"

    text = str(code)
    if text != page.text:
        page.text = text
        return page

    return None


concur = ConcurrentBot(
    treat,
    "replace {{[[Template:l|l]]}} with {{[[Template:alt|alt]]}} in alternative forms sections",
    PreloadingGenerator(iter_pages()),
)

concur.start()
