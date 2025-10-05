"""
Interactive script for moving a category.
"""

import difflib
import re
import signal
import sys
from InquirerPy import inquirer
import pywikibot
from pywikibot import pagegenerators
from pywikibot.page import BasePage

# pywikibot has an obnoxiously long traceback for sigint, just handle it here
signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

print("\033[3m(hint: the namespace is automatically added)\033[0m")
target = inquirer.text(
    message="Moving members of this category:",
).execute()

cat_target = "Category:" + target

site = pywikibot.Site()
cat = pywikibot.Category(site, cat_target)
if not cat.exists():
    print(f"\033[31mpage {cat_target} does not exist\033[0m")
    sys.exit(1)

renamed = inquirer.text(
    message="To this category:",
).execute()

cat_renamed = "Category:" + renamed

options = inquirer.checkbox(
    message="Configuration:",
    choices=[
        {"name": "move category page when done", "value": "move_cat"},
        {"name": "manually review changes", "value": "review"},
        {"name": "dry run (don't save any pages)", "value": "dry"},
    ],
    instruction="(arrow keys to move, space to select, enter to submit)",
).execute()

gen = pagegenerators.CategorizedPageGenerator(cat)

is_topic = re.match(r"([^:]+):(.+)", target)

if is_topic:
    lang, topic = is_topic.groups()
    matched = re.match(r"[^:]+:(.+)", renamed)

    if matched is None:
        raise TypeError

    new_topic = matched.groups()[0]

    update = re.compile(
        f"\\[\\[cat(?:egory)?:{lang}:{topic}\\]\\]|"
        + f"{{{{(?:topics|c)\\|{lang}\\|([^}}]*?){topic}}}}}",
        flags=re.I,
    )

    def repl(m):
        return f"{{{{C|{lang}|{m.groups()[0] or ''}{new_topic}}}}}"
else:
    update = re.compile(f"\\[\\[cat(?:egory)?:{target}\\]\\]", flags=re.I)

    def repl(_):
        return f"[[{cat_renamed}]]"


def diff(a: str, b: str) -> str:
    """
    Generate a line-by-line unified diff between two strings, highlighted in green and red.
    """

    lines_a = a.splitlines()
    lines_b = b.splitlines()

    def colour(line):
        if line.startswith("+") and not line.startswith("+++"):
            return f"\033[32m{line}\033[0m"
        if line.startswith("-") and not line.startswith("---"):
            return f"\033[31m{line}\033[0m"
        return line

    diff_lines = difflib.unified_diff(
        lines_a,
        lines_b,
        fromfile="old",
        tofile="new",
        lineterm="",
    )

    coloured = [colour(line) for line in diff_lines]
    return "\n".join(coloured)


for page in pagegenerators.PreloadingGenerator(gen, 10):
    text = update.sub(repl, page.text)

    if "review" in options:
        print()
        print(diff(page.text, text) or "\033[3m(no changes made)\033[0m")
        if input("\033[34msave?\033[0m [Y/n]: ") == "n":
            continue

    summary = f"Moving category [[:{cat_target}]] to [[:{cat_renamed}]]"
    if "dry" not in options:
        page.text = text
        page.save(summary)
    else:
        print(summary)

if "move_cat" in options:
    page = BasePage(site, title=cat_target)
    page.move(
        cat_target,
        f"Moving category [[:{cat_target}]] to [[:{cat_renamed}]]",
        movesubpages=False,
    )
