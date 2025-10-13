"""
CLI or library for searching for patterns in page text with the pages-meta-current dump.
See dump_grep --help for more.
This script searches dumps/latest.xml. This should be enwiktionary-YYYYMMDD-pages-meta-current.

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

from argparse import ArgumentParser
import bz2
import os
import re
import requests
import signal
import sys
from typing import Callable
from lxml import etree
from tqdm import tqdm

signal.signal(signal.SIGINT, lambda *_: sys.exit(130))


def fetch(
    base: str = "https://dumps.wikimedia.org/enwiktionary/latest/",
):
    filename = "enwiktionary-latest-pages-meta-current.xml.bz2"
    url = base + filename

    response = requests.get(url, stream=True)
    response.raise_for_status()

    length_header = response.headers.get("content-length")
    total = None
    dynamic_ncols = False

    if length_header is not None:
        total = int(length_header)
    else:
        dynamic_ncols = True

    filename_display = filename[0:20] + "..."

    print("Downloading...")

    with (
        open("dumps/" + filename, "wb") as f,
        tqdm(
            total=total,
            dynamic_ncols=dynamic_ncols,
            unit="B",
            unit_scale=True,
            desc=filename_display,
        ) as progress,
    ):
        for chunk in response.iter_content(chunk_size=8 * 1024):
            if chunk:
                f.write(chunk)
                progress.update(8 * 1024)

    print("Decompressing...")

    with (
        open("dumps/" + filename[:-4], "wb") as decomp,
        bz2.BZ2File("dumps/" + filename, "rb") as comp,
    ):
        for data in iter(lambda: comp.read(100 * 1024), b""):
            decomp.write(data)

    os.remove("dumps/" + filename)
    os.remove("dumps/latest.xml")  # remove any previous symlink

    os.symlink("dumps/" + filename[:-4], "dumps/latest.xml")


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

    exp: re.Pattern

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
        n += count
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


def cli():
    """
    Command-line entrypoint.
    """

    parser = ArgumentParser(
        prog="dump_grep",
        description="Script for searching Wikimedia dumps",
    )

    parser.add_argument(
        "query",
        nargs="?",
        help="regex (see documentation for the re module)",
    )

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

    parser.add_argument(
        "--fetch",
        action="store_true",
        help="download latest dump and link it to dumps/latest.xml",
    )

    args = parser.parse_args()

    if not args.query and not args.fetch:
        parser.error("one of query or --format must be passed")

    if args.fetch and not args.query:
        return fetch()

    if args.fetch:
        fetch()

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


if __name__ == "__main__":
    cli()
