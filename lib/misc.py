"""
Miscellaneous utilities.

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

__all__ = ["diff", "merge_templates"]

import difflib
from mwparserfromhell.nodes import Template
from mwparserfromhell.wikicode import Wikicode


def diff(a: str, b: str) -> str:
    """
    Generate a line-by-line unified diff between two strings,
    highlighted in green and red.
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


def merge_templates(code: Wikicode, templates: list[Template]) -> None:
    """
    Merge a list of templates into one, preserving the first
    langcode parameter. Used for merging topic and cln
    templates.
    """
    cats: dict[str, Template] = {}

    for template in templates:
        lang = str(template.get(1))
        categories = template.params[1:]

        if cats.get(lang) is None:
            cats[lang] = template
            continue

        code.remove(template)

        for category in categories:
            at = len(cats[lang].params) + 1
            cats[lang].add(at, category)
