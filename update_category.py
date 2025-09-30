import difflib
from InquirerPy import inquirer
import pywikibot
from pywikibot import pagegenerators
from pywikibot.page import BasePage
import re
import signal
import sys

# pywikibot has an obnoxiously long traceback for sigint, just handle it here
signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

print("\033[3m\033[1;30m(hint: the namespace is automatically added)\033[0m")
target = input("\033[34mmoving members of category\033[0m > ")
cat_target = "Category:" + target

site = pywikibot.Site()
cat = pywikibot.Category(site, cat_target)
if not cat.exists():
    print(f"\033[31mpage {cat_target} does not exist\033[0m")
    sys.exit(1)

renamed = input("\033[34mto here\033[0m > ")

cat_renamed = "Category:" + renamed

options = inquirer.checkbox(
    message="configuration:",
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
    new_topic = re.match(r"[^:]+:(.+)", renamed).groups()[0]

    update = re.compile(f"\\[\\[cat(?:egory)?:{lang}:{topic}\\]\\]|{{{{(?:topics|c)\\|{lang}\\|([^}}]*?){topic}}}}}", flags = re.I)
    def repl(match):
        return f"{{{{C|{lang}|{match.groups()[0] or ""}{new_topic}}}}}"
else:
    update = re.compile(f"\\[\\[cat(?:egory)?:{target}\\]\\]", flags = re.I)
    repl = f"[[{cat_renamed}]]"

def diff(A: str, B: str) -> str:
    linesA = A.splitlines()
    linesB = B.splitlines()

    def colour(line):
        if line.startswith('+') and not line.startswith('+++'):
            return f"\033[32m{line}\033[0m"
        elif line.startswith('-') and not line.startswith('---'):
            return f"\033[31m{line}\033[0m"
        else:
            return line

    diff = difflib.unified_diff(
        linesA,
        linesB,
        fromfile="old",
        tofile="new",
        lineterm="",
    )

    coloured = [colour(line) for line in diff]
    return "\n".join(coloured)

for page in pagegenerators.PreloadingGenerator(gen, 10):
    text = update.sub(repl, page.text)

    if "review" in options:
        print()
        print(diff(page.text, text) or "\033[1;30m(no changes made)\033[0m")
        if input("\033[34msave?\033[0m [Y/n]: ") == "n":
            continue
    
    summary = f"Moving category [[:{cat_target}]] to [[:{cat_renamed}]]"
    if "dry" not in options:
        page.text = text
        page.save(summary)
    else:
        print(summary)

if "move_cat" in options:
    page = BasePage(site, title = cat_target)
    page.move(cat_target, f"Moving category [[:{cat_target}]] to [[:{cat_renamed}]]", movesubpages = False)
