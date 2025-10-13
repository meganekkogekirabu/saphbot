"""
Interactive script for moving a category.

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
import signal
import sys
from InquirerPy import inquirer
import pywikibot
from pywikibot import pagegenerators
from pywikibot.page import BasePage
from lib.misc import diff

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

    def _repl(m):
        return f"{{{{C|{lang}|{m.groups()[0] or ''}{new_topic}}}}}"
else:
    update = re.compile(f"\\[\\[cat(?:egory)?:{target}\\]\\]", flags=re.I)

    def _repl(_):
        return f"[[{cat_renamed}]]"


repl = _repl


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
