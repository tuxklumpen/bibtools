import click as cl
import pathlib as pl

from .dblp import dblpfunctions as dblpf
from .bibformat import bibformat

@cl.group()
def cli():
    pass

@cli.command()
@cl.option("-i", "--id", type=str, default=None, help="The idea of the dblp page to fetch.")
@cl.argument("output", type=cl.Path(writable=True, dir_okay=False, path_type=pl.Path))
def dblpauthor(id, output):
    dblp = dblpf.DBLP()
    with open(output, "w") as f:
        if id:
            bib = dblp.bibliography_by_id(id)
            if format:
                bib = bibformat(bib)
                
            f.write(bib)

@cli.command()
@cl.option("-p", "--start-page", type=str, default="", help="Provide a page to resume execution from. If both start-page and start-link are given its assumed that start-link is on start-page.")
@cl.option("-l", "--start-link", type=str, default="", help="Provide a link to resume execution from.")
@cl.argument("output", type=cl.Path(writable=True, dir_okay=False, path_type=pl.Path))
def buildjournallist(output, start_page, start_link):
    with open(output, "a") as f:
        dblpf.bigfatjournalist(f, start_page, start_link)

@cli.command()
@cl.option("--remove-dblp", type=bool, default=True, help="Delete bibsource, timestamp, and biburl.")
@cl.option("--remove-url-if-doi", type=bool, default=True, help="Remove url field if doi is present.")
@cl.option("--expand-journal", type=bool, default=True, help="Try to expand abbreviated journal entries.")
@cl.argument("input", type=cl.Path(exists=True, dir_okay=False, path_type=pl.Path))
@cl.argument("output", type=cl.Path(writable=True, dir_okay=False, path_type=pl.Path))
def format(remove_dblp, remove_url_if_doi, expand_journal, dblp_booktitles, input, output):
    inputbib = ""
    with open(input, "r") as inf:
        inputbib = inf.read()
    
    with open(output, "w") as outf:
        outf.write(bibformat(inputbib, remove_dblp, remove_url_if_doi, expand_journal, dblp_booktitles))