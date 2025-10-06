"""
CLI or library for searching for patterns in page text with the pages-meta-current dump.
See dump_grep --help for more.
This script searches dumps/latest.xml. This should be enwiktionary-YYYYMMDD-pages-meta-current.
"""

from argparse import ArgumentParser
import re
import signal
import sys
from typing import Callable
from lxml import etree
from tqdm import tqdm

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))


def grep(
    query: str,
    flags: int,
    pagename: bool,
    callback: Callable,
    iterator,
):
    """
    Main grepping function. This should not be called directly.
    Use the entrypoints grep_cli or grep_lib.
    """

    if not pagename:
        exp = re.compile(query, flags=flags)

    for _, elem in iterator:
        title = elem.find("{*}title").text
        text = elem.find("{*}revision/{*}text").text

        if not text:
            elem.clear()
            continue

        if pagename:
            dyn = query.replace("{{PAGENAME}}", re.escape(title))
            exp = re.compile(dyn, flags=flags)

        if not exp.search(text):
            elem.clear()
            continue

        callback(title)

        elem.clear()
        while elem.getprevious() is not None:
            del elem.getparent()[0]


def grep_lib(
    query: str,
    flags: int = 0,
    pagename: bool = False,
) -> list:
    """
    Entrypoint to grep for other Python scripts.
    """

    iterator = etree.iterparse("dumps/latest.xml", events=("end",), tag=("{*}page"))
    titles = []

    def callback(title: str):
        nonlocal titles
        titles.append(title)

    grep(query, flags, pagename, callback, iterator)

    return titles


def grep_cli(
    query: str,
    flags: int = 0,
    pagename: bool = False,
    fmt: str = "{}",
    output=sys.stdout,
    count: bool = False,
):
    """
    Entrypoint to grep for the command line.
    """

    n = 0

    def callback(title: str):
        nonlocal n
        nonlocal count
        n += count  # noqa
        if not count:
            print(fmt.format(title), file=output)

    context = etree.iterparse("dumps/latest.xml", events=("end",), tag=("{*}page"))

    if output == sys.stdout and not count:
        iterator = context  # don't use tqdm when writing to stdout, it looks stupid
    else:
        # fixme: would be nice to fetch total dynamically somehow
        # for now, just manually run `grep page dumps/latest.xml`
        iterator = tqdm(context, unit="ppg", desc="Searching", total=10363325)

    grep(query, flags, pagename, callback, iterator)

    if count:
        print(n)


if __name__ == "__main__":
    parser = ArgumentParser(
        prog="dump_grep",
        description="Script for searching Wikimedia dumps",
    )

    parser.add_argument("query", help="regex (see documentation for the re module)")

    parser.add_argument(
        "-f",
        "--flags",
        help="regex flags to apply to the query, e.g. 'mi' for multiline and case-insensitive",
    )

    parser.add_argument(
        "--pagename",
        action="store_true",
        help="if enabled, {{PAGENAME}} in the query is dynamically substituted for the pagename for each page",
    )

    parser.add_argument(
        "--format",
        help="format to output pages in, e.g. '* [[{}]]' to print titles out like a wikitext list",
    )

    parser.add_argument("-o", "--output", help="output file (defaults to stdout)")

    parser.add_argument(
        "-c",
        "--count",
        action="store_true",
        help="if enabled, prints out a count of matching pages rather than a list",
    )

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
        with open(args.output, "w", encoding="utf-8") as file:
            grep_cli(
                args.query,
                flags,
                pagename=args.pagename,
                fmt=args.format or "{}",
                output=file,
                count=args.count,
            )
    else:
        grep_cli(
            args.query,
            flags,
            pagename=args.pagename,
            fmt=args.format or "{}",
            count=args.count,
        )
