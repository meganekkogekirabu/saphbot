import pywikibot
import re
from datetime import timedelta
from pywikibot.page import BasePage

ignore = [] 

with open("lists/babel_cat_ignore.txt", "r") as file:
    for line in file:
        ignore.append(line)

site = pywikibot.Site()
tl_page = pywikibot.Page(site, "Template:Babel")
gen = BasePage(tl_page).getReferences(only_template_inclusion=True, namespaces=2)

for page in gen:
    title = page.title()
    
    if "/" not in title and title not in ignore:
        last_edit = pywikibot.User(site, title).last_edit
        
        try:
            delta = (site.server_time() - last_edit[2]) >= timedelta(days=730)
            
            if delta and "inactive=1" not in page.text:
                page.text = re.sub(r"({{babel[^}]+)", r"\1|inactive=1", page.text, flags = re.I)
                page.save("mark users whose last contribution was more than 2 years ago as inactive in Babel")
        
        except:
            # Probably a redirect from a rename; just skip.
            continue
