import pywikibot
import re
from datetime import timedelta
from pywikibot.pagegenerators import AllpagesPageGenerator

site = pywikibot.Site()
tl_page = pywikibot.Page(site, "Template:Babel")
gen = pywikibot.page.BasePage(tl_page).getReferences(only_template_inclusion=True, namespaces=2)

for page in gen:
    title = page.title()
    
    if "/" not in title:
        last_edit = pywikibot.User(site, title).last_edit
        
        try:
            delta = (site.server_time() - last_edit[2]) >= timedelta(days=730)
            
            if delta and "Babel" in page.text and "inactive" not in page.text:
                page.text = re.sub(r"({{Babel[^}]+)", r"\1|inactive=1", page.text)
                page.save("mark users whose last contribution was more than 2 years ago as inactive in Babel")
                
            elif not delta and "inactive" in page.text:
                page.text = re.sub(r"({{Babel[^}]+)\|inactive=1", r"\1")
                page.save("enable Babel categorisation, which was disabled despite last edit being recent")
        
        except:
            # Probably a redirect from a rename; just skip.
            continue
