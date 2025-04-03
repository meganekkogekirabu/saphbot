import pywikibot
import re
from datetime import timedelta
from pywikibot.pagegenerators import AllpagesPageGenerator

site = pywikibot.Site()
gen = AllpagesPageGenerator(namespace=2, site=site)

for page in gen:
    title = page.title()
    
    if "/" not in title:
        last_edit = pywikibot.User(site, title).last_edit
        
        try:
            delta = (site.server_time() - last_edit[2]) >= timedelta(days=730)
            
            if delta and "Babel" in page.text and "nocat" not in page.text:
                page.text = re.sub(r"^(?!<!-- ?)({{Babel[^}]+)", r"\1|nocat=1", page.text, flags =  re.MULTILINE)
                page.save("testing: disable Babel categorisation for users whose last contribution was more than 2 years ago")
                
            elif not delta and "nocat" in page.text:
                page.text = re.sub(r"({{Babel[^}]+)\|nocat=1", r"\1")
                page.save("testing: enable Babel categorisation, which was disabled despite last edit being recent")
        
        except:
            # Probably a redirect from a rename; just skip.
            continue