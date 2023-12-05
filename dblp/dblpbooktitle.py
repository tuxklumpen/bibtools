from bibtexparser.model import Entry, Field, Block
from bibtexparser import middlewares as mw
import datetime as dt
from dataclasses import dataclass
import abc
import re

month = {
    "January" : 1,
    "Februray" : 2,
    "March" : 3,
    "April" : 4,
    "May" : 5,
    "June" : 6,
    "July" : 7,
    "August" : 8,
    "September" : 9,
    "October" : 10,
    "November" : 11,
    "December" : 12
}

@dataclass
class Booktitle(abc.ABC):
    iteration: str
    abbreviation: str
    confname: str
    subtitle: str
    location: str
    start: dt.date
    end: dt.date

    def format(self) -> str:
        return f"Proceedings of the {self.iteration} {self.confname} ({self.abbreviation}'{self.start.year})"

    @staticmethod
    def applies(booktitle: str) -> bool:
        return True

    @abc.abstractstaticmethod
    def make(booktitle: str) -> "Booktitle":
        pass

class GDNVBooktitle(Booktitle):
    @staticmethod
    def applies(booktitle: str) -> bool:
        if booktitle.startswith("Graph Drawing and Network Visualization"):
            return True
        
        return False
    
    @staticmethod
    def make(booktitle: str) -> "GDNVBooktitle":
        booktitle = ' '.join(booktitle.replace("\n", "").split())
        matched = re.match(r"Graph Drawing and Network Visualization - (?P<iteration>.+) International Symposium, GD (?P<year>[0-9]{4}), (?P<location>.+), (?P<month>[A-Z][a-z]+) (?P<start>[0-9]+)-(?P<end>[0-9]+), [0-9]{4}, (?P<subtitle>.*)$", booktitle)

        start = dt.date(*map(int, [matched.group("year"), month[matched.group("month")], matched.group("start")]))
        end = dt.date(*map(int, [matched.group("year"), month[matched.group("month")], matched.group("end")]))

        return GDNVBooktitle(
            matched.group("iteration"),
            "GD",
            "International Symposium on Graph Drawing and Network Visualization",
            matched.group("subtitle"),
            matched.group("location"),
            start,
            end
        )
    
class STACSBooktitle(Booktitle):
    @staticmethod
    def applies(booktitle: str) -> bool:
        if "Symposium on Theoretical Aspects of Computer Science" in booktitle:
            return True
        
        return False
    
    @staticmethod
    def make(booktitle: str) -> "GDNVBooktitle":
        booktitle = ' '.join(booktitle.replace("\n", "").split())
        print(booktitle)
        print(re.match(r"(?P<iteration>.+) Symposium on Theoretical Aspects of Computer Science.*$", booktitle).groups())

        return
        matched = re.match(r"(?P<iteration>.+) (?:International |\b)Symposium on Theoretical Aspects of Computer Science, STACS (?P<year>[0-9]{4}), (?P<month>[A-Z][a-z]+) (?P<start>[0-9]+)-(?P<end>[0-9]+), [0-9]{4}, (?P<location>.+)$", booktitle)
        print(matched.groups())

        start = dt.date(*map(int, [matched.group("year"), month[matched.group("month")], matched.group("start")]))
        end = dt.date(*map(int, [matched.group("year"), month[matched.group("month")], matched.group("end")]))

        return GDNVBooktitle(
            matched.group("iteration"),
            "GD",
            "International Symposium on Graph Drawing and Network Visualization",
            matched.group("subtitle"),
            matched.group("location"),
            start,
            end
        )


class DBLPBooktitleParts(mw.middleware.BlockMiddleware):
    def __init__(
        self,
        allow_inplace_modification: bool = True
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    @staticmethod
    def metadata_key() -> str:
        """Identifier of the middleware.

        This key is used to identify the middleware in a blocks metadata.
        """
        return "expand_journal"
    
    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        if entry.entry_type == "inproceedings":
            booktitle = entry.fields_dict['booktitle'].value
            for cls in Booktitle.__subclasses__():
                if cls.applies(booktitle):
                    entry.fields_dict['booktitle'].value = cls.make(booktitle)
                    break

        entry.parser_metadata[self.metadata_key()] = True

        return entry
    
class DBLPBooktitleMerge(mw.middleware.BlockMiddleware):
    def __init__(
        self,
        allow_inplace_modification: bool = True
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )

    @staticmethod
    def metadata_key() -> str:
        """Identifier of the middleware.

        This key is used to identify the middleware in a blocks metadata.
        """
        return "expand_journal"
    
    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        if entry.entry_type == "inproceedings":
            booktitle = entry.fields_dict['booktitle'].value
            entry.fields_dict['booktitle'].value = booktitle.format()

        entry.parser_metadata[self.metadata_key()] = True

        return entry
