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
        print(body.get("error"))
        raise Exception(f"Could not find page {title}")
        return {}
    
    return json.loads(body["parse"]["wikitext"])

class Languages:
    def __init__(self):
        self.canonical_names = {}
        self.language_codes = {}

    def get_canonical_names(self):
        if self.canonical_names == {}:
            self.canonical_names = json_from_wikitext("Module:languages/canonical names.json")
        return self.canonical_names
    
    def get_codes(self):
        if self.language_codes == {}:
            self.language_codes = json_from_wikitext("Module:languages/code to canonical name.json")
        return self.language_codes
    
    def get_canonical_name(self, lang):
        return self.canonical_names.get(lang)