import csv
from .middleware import *
from .dblp.dblpconstants import DBLP_EXTRA_FIELDS
import bibtexparser as btxp

def bibformat(bibliography: str, remove_dblp: bool = True, remove_url_if_doi: bool = True, expand_journal: bool = True) -> str:
    middleware = [
                # transforms {\"o} -> ö, removes curly braces, etc.
                mw.LatexDecodingMiddleware(),
                # transforms apr -> 4 etc.
                mw.MonthIntMiddleware(True),
                # turns author field with multiple authors into a list
                mw.SeparateCoAuthors(),
                # splits author names into {first, von, last, jr}
                mw.SplitNameParts(),
            ]
    
    if remove_dblp:
        # clean DBLP fields in entries
        middleware.append(DeleteFields(delete_fields=DBLP_EXTRA_FIELDS))

    if remove_url_if_doi:
        # clean url if doi not present
        middleware.append(DeleteFieldsOrdered(delete_fields=["doi", "url"]))

    if expand_journal:
        journallist = {}
        longs = set()
        with open("mybigfatjournallist2.csv") as f:
            journals = csv.DictReader(f, delimiter=';')
            for j in journals:
                journallist[j['short']] = j['long']
                longs.add(j['long'])

        # Expand short journals
        middleware.append(ExpandJournal(short_to_long=journallist, long=longs))

    library = btxp.parse_string(
        bibliography,
        append_middleware=middleware
    )

    formatmiddleware = []

    formatmiddleware += [mw.MergeNameParts(), mw.MergeCoAuthors(), mw.LatexEncodingMiddleware()]

    formatted = btxp.write_string(library, 
            prepend_middleware=formatmiddleware
        )
    
    return formatted