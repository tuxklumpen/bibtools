from typing import List, Dict, Set

import click as cl

from bibtexparser.model import Entry, Field, Block
from bibtexparser import middlewares as mw

class ExpandJournal(mw.middleware.BlockMiddleware):
    def __init__(
        self,
        allow_inplace_modification: bool = True,
        short_to_long: Dict[str, str] = {},
        long: Set[str] = set()
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )
        self.short_to_long = short_to_long
        self.long = long

    @staticmethod
    def metadata_key() -> str:
        """Identifier of the middleware.

        This key is used to identify the middleware in a blocks metadata.
        """
        return "expand_journal"

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        if entry.entry_type == "article":
            current = entry.fields_dict["journal"].value
            if not (current in self.long):
                if current == "CoRR":
                    pass
                elif current in self.short_to_long:
                    entry.fields_dict["journal"].value = self.short_to_long[current]
                else:
                    long = cl.prompt(f"Could not find {current} in my list of journals. Add a long form or leave empty to skip", default="")
                    if long != "":
                        entry.fields_dict["journal"].value = long
                        self.journallist[current] = long # TODO Store the moficiation actually

        entry.parser_metadata[self.metadata_key()] = True

        return entry

class DeleteFields(mw.middleware.BlockMiddleware):
    def __init__(
        self,
        allow_inplace_modification: bool = True,
        delete_fields: List[str] = []
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )
        self.delete_fields = delete_fields

    @staticmethod
    def metadata_key() -> str:
        """Identifier of the middleware.

        This key is used to identify the middleware in a blocks metadata.
        """
        return "delete_fields"

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        entry.fields = list(filter(lambda f: not f.key in self.delete_fields , entry.fields))
        entry.parser_metadata[self.metadata_key()] = True

        return entry
    
class DeleteFieldsOrdered(mw.middleware.BlockMiddleware):
    def __init__(
        self,
        allow_inplace_modification: bool = True,
        delete_fields: List[str] = []
    ):
        super().__init__(
            allow_inplace_modification=allow_inplace_modification,
            allow_parallel_execution=True,
        )
        self.delete_fields = delete_fields

    @staticmethod
    def metadata_key() -> str:
        """Identifier of the middleware.

        This key is used to identify the middleware in a blocks metadata.
        """
        return "delete_fields_ordered"

    def transform_entry(self, entry: Entry, *args, **kwargs) -> Block:
        startfrom = 0
        while not (self.delete_fields[startfrom] in entry.fields_dict.keys()):
            startfrom += 1
            if startfrom == len(self.delete_fields):
                break

        if startfrom == len(self.delete_fields):
            return entry
        else:
            entry.fields = list(filter(lambda f: not f.key in self.delete_fields[startfrom+1:], entry.fields))
            entry.parser_metadata[self.metadata_key()] = True

            return entry