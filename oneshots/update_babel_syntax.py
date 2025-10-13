"""
Update legacy Babel gender switch syntax {masc+fem+(neut)} to {masc/fem(/neut)}.

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
from pywikibot.pagegenerators import TextIOPageGenerator, PreloadingGenerator

gen = TextIOPageGenerator("lists/private/babel_subpages.txt")

exp = re.compile("{([^+\\n]+)\\+([^+\\n]+)\\+([^+}\\n]+)?}")


def repl(match: re.Match[str]) -> str:
    masc, fem, neut = match.groups()

    if neut is not None:
        return f"{{{masc}/{fem}/{neut}}}"
    else:
        return f"{{{masc}/{fem}}}"


for page in PreloadingGenerator(gen):
    page.text = exp.sub(repl, page.text)
    page.save("update Babel gender switch syntax")
