"""
Represents an ontology
"""

import networkx as nx
import logging
import obographs.obograph_util as obograph_util
import obographs.sparql.sparql_ontology
from obographs.ontol import Ontology
from obographs.sparql.sparql_ontology import EagerRemoteSparqlOntology
import os
import subprocess

class OntologyFactory():
    """
    Creates an ontology
    """
    def __init__(self, handle=None):
        """
        initializes based on an ontology name
        """
        self.handle = handle

    def create(self, handle=None):
        ont = None
        logging.info("Determining strategy to load '{}' into memory...".format(handle))
        
        if handle.find(".") > 0 and os.path.isfile(handle):
            logging.info("Fetching obograph-json file from filesystem")
            g = obograph_util.convert_json_file(handle)
            ont = Ontology(handle=handle, graph=g)
        elif handle.startswith("obo:"):
            logging.info("Fetching from OBO PURL")
            if handle.find(".") == -1:
                handle += '.owl'
            fn = '/tmp/'+handle
            if not os.path.isfile(fn):
                url = handle.replace("obo:","http://purl.obolibrary.org/obo/")
                cmd = ['owltools',url,'-o','-f','json',fn]
                cp = subprocess.run(cmd, check=True)
                logging.info(cp)
            else:
                logging.info("using cached file: "+fn)
            g = obograph_util.convert_json_file(fn)
            ont = Ontology(handle=handle, graph=g)
        else:
            logging.info("Fetching from SPARQL")
            ont = EagerRemoteSparqlOntology(handle=handle)
            #g = get_digraph(handle, None, True)
        return ont
        
        
