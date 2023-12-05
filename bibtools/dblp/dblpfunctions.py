import requests as rq
from typing import TextIO, Tuple
import time
import pathlib as pl
from bs4 import BeautifulSoup
import re
from dataclasses import dataclass, field
from .dblpconstants import *
from urllib.parse import urlparse

@dataclass
class DBLP:  
    # Timeout for timeout seconds if we made more than requestlimit requests in the last reset seconds
    timeout: int = 60 
    reset: int = 60
    requestlimit: int = 50

    _maderequests: int = 0
    _lastrequest: float = field(default_factory=time.time)

    def __init__(self):
        self._lastrequest = time.time()

    def bibliography_by_id(self, id: str) -> str:
        return self._make_request(AUTHOR_BIB.format(id))

    def journal_list(self, pos: str = "") -> str:
        return self._make_request(JOURNAL_LIST.format(pos))
    
    def journal_names(self, journal) -> Tuple[str, str]:
        html = self._make_request(JOURNAL_MAIN.format(journal))
        soup = BeautifulSoup(html, 'html.parser')
        h1title = soup.find("h1")
        noteline = soup.find("div", "note-line")
        infos = soup.find(id="info-section")

        title = h1title.text if not noteline else noteline.text
        iso4 = title
        abbreviation = ""

        if infos:
            infos = infos.find("li")
            match = re.search(r"^ISO 4 abbr.: (.*)issn.*", infos.text)
            if match:
                iso4 = match.group(1).strip()

        match = re.search(r"^.*(\(.+\))$", title)
        if match:
            abbreviation = match.group(1).strip()
            title = title.replace(abbreviation, "").strip()

        return abbreviation[1:-1], iso4, title

    def _make_request(self, url: str) -> str:
        if (time.time() - self._lastrequest) <= self.reset:
            if self._maderequests >= self.requestlimit:
                print(f"Made too many requests in the last {self.reset} seconds, sleeping for {self.timeout} seconds.")
                j = 0
                while j <= self.timeout:
                    print(f"{self.timeout - j} seconds remaining", end="\r")
                    j += 1
                    time.sleep(1)

                self._maderequests = 0
            else:
                self._maderequests += 1
        else:
            self._maderequests = 0
            
        self._lastrequest = time.time()

        return rq.get(url).content.decode()

def bigfatjournalist(output: TextIO, startpage: str = "", lastlink: str = "", delim: str = ";", dblpapi: DBLP = DBLP()):
    foundlastlink = True if lastlink == "" else False
    print(lastlink)

    pos = startpage
    while True:
        html = dblpapi.journal_list(pos)
        soup = BeautifulSoup(html, 'html.parser')
        tip = soup.find(id="browse-journals-output")
        journals = tip.find_all("li")

        print(f"Currently doing page {pos}")

        for i, journal in enumerate(journals):
            print(f"{i}/{len(journals)}", end="\r")
            link = journal.a['href']
            jref = pl.Path(urlparse(link).path).name

            if not lastlink and lastlink.startswith(link):
                foundlastlink = True

            if foundlastlink:
                abbrv, short, long = dblpapi.journal_names(jref)
                output.write(f"{abbrv}{delim}{short}{delim}{long}\n")
                output.flush()

        next = tip.find_all("a")[-1]
        if not "next" in next.text:
            print(f"{next} looks not like the right link, aborting")
            break
        else:
            print(next['href'])
            pos = next['href'].split("=")[-1]