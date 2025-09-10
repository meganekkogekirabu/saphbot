# Utilities for working with en:wikt:Module:languages.

import requests
import json

class Languages:
    def __init__(self):
        self.canonical_names = None

    def get_canonical_names(self):
        response = requests.get(
                "https://en.wiktionary.org/w/api.php?action=parse&format=json&page=Module%3Alanguages%2Fcanonical%20names.json&prop=wikitext&formatversion=2",
                headers={
                    "User-Agent": "SaphBot",
                })

        body = response.json()
        self.canonical_names = json.loads(body["parse"]["wikitext"])
