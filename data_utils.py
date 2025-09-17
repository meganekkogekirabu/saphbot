# Utilities for working with en:wikt:Module:languages.

import requests
import json

def json_from_wikitext(title):
    response = requests.get(
        f"https://en.wiktionary.org/w/api.php",
        {
            "action": "parse",
            "format": "json",
            "formatversion": "2",
            "page": title,
            "prop": "wikitext",
        },
        headers={
            "User-Agent": "SaphBot",
        })
    
    if response.status_code != 200:
        raise Exception(f"API returned status code {response.status_code}")
        return {}
    
    body = response.json()
    if body.get("error"):
        raise Exception(f"Could not find page {title}:", body["error"])
        return {}
    
    return json.loads(body["parse"]["wikitext"])


class WiktData:
    def __init__(self, module):
        self.canonical_names = {}
        self.language_codes = {}
        self.module = module

    def get_canonical_names(self):
        if self.canonical_names == {}:
            self.canonical_names = json_from_wikitext(f"Module:{self.module}/canonical names.json")
        return self.canonical_names
    
    def get_codes(self):
        if self.language_codes == {}:
            self.language_codes = json_from_wikitext(f"Module:{self.module}/code to canonical name.json")
        return self.language_codes
    
    def get_by_canonical_name(self, query):
        return self.canonical_names.get(query)
        
class Languages(WiktData):
    def __init__(self):
        super().__init__("languages")

class Scripts(WiktData):
    def __init__(self):
        super().__init__("scripts")