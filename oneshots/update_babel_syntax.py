import re
import pywikibot
from pywikibot.pagegenerators import TextIOPageGenerator, PreloadingGenerator

site = pywikibot.Site()
gen = TextIOPageGenerator("lists/private/babel_subpages.txt")

exp = re.compile("{([^+\\n]+)\\+([^+\\n]+)\\+([^+}\\n]+)?}")


def repl(match: str) -> str:
    masc, fem, neut = match.groups()

    if neut is not None:
        return f"{{{masc}/{fem}/{neut}}}"
    else:
        return f"{{{masc}/{fem}}}"


for page in PreloadingGenerator(gen):
    page.text = exp.sub(repl, page.text)
    page.save("update Babel gender switch syntax")
