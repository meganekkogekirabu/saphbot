from argparse import ArgumentParser
from lxml import etree
import re
import signal
import sys
from tqdm import tqdm

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))

def grep(query: str, flags: int = 0, pagename: bool = False, fmt: str = "{}", output = sys.stdout, count: bool = False):    
    # latest.xml should be enwiktionary-YYYYMMDD-pages-meta-current.xml
    context = etree.iterparse("dumps/latest.xml", events=("end",), tag=("{*}page"))

    if not pagename:
        exp = re.compile(query, flags = flags)
    
    n = 0
    
    if output == sys.stdout and not count:
        iterator = context  # don't use tqdm when writing to stdout, it looks stupid
    else:
        # fixme: would be nice to fetch total dynamically somehow
        # for now, just manually run `grep page dumps/latest.xml`
        iterator = tqdm(context, unit = "ppg", desc = "Searching", total = 10363325)

    for _, elem in iterator:
        title = elem.find("{*}title").text
        text = elem.find("{*}revision/{*}text").text

        if not text:
            elem.clear()
            continue

        if pagename:
            dyn = query.replace("{{PAGENAME}}", re.escape(title))
            exp = re.compile(dyn, flags = flags)

        if not exp.search(text):
            elem.clear()
            continue
        
        n += count
        if not count:
            print(fmt.format(title), file = output)

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]
    
    if count:
        print(n)

if __name__ == "__main__":
    parser = ArgumentParser(
        prog = "dump_grep",
        description = "Script for searching Wikimedia dumps",
    )

    parser.add_argument("query",
        help = "regex (see documentation for the re module)")

    parser.add_argument("-f", "--flags",
        help = "regex flags to apply to the query, e.g. 'mi' for multiline and case-insensitive")

    parser.add_argument("--pagename", action = "store_true",
        help = "if enabled, {{PAGENAME}} in the query is dynamically substituted for the pagename for each page")

    parser.add_argument("--format",
        help = "format to output pages in, e.g. '* [[{}]]' to print titles out like a wikitext list")

    parser.add_argument("-o", "--output",
        help = "output file (defaults to stdout)")
    
    parser.add_argument("-c", "--count", action = "store_true",
        help = "if enabled, prints out a count of matching pages rather than a list")
    
    args = parser.parse_args()

    flagmap = {
        "a": re.ASCII,
        "i": re.IGNORECASE,
        "l": re.LOCALE,
        "m": re.MULTILINE,
        "s": re.DOTALL,
        "u": re.UNICODE,
        "x": re.VERBOSE,
    }

    args.flags = list(args.flags.lower()) if args.flags else ""

    vals = [flagmap[item] for item in args.flags if item in flagmap]
    flags = 0
    for f in vals:
        flags |= f

    if args.output:
        with open(args.output, "w", encoding = "utf-8") as file:
            grep(args.query, flags, pagename = args.pagename, fmt = args.format or "{}", output = file, count = args.count)
    else:
        grep(args.query, flags, pagename = args.pagename, fmt = args.format or "{}", count = args.count)
