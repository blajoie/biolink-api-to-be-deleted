"""
Factory class for generating ontology objects based on a variety of handle types
"""

import networkx as nx
import logging
import obographs.obograph_util as obograph_util
import obographs.sparql.sparql_ontology
from obographs.ontol import Ontology
from obographs.sparql.sparql_ontology import EagerRemoteSparqlOntology
import os
import subprocess
import hashlib
from cachier import cachier
import datetime

SHELF_LIFE = datetime.timedelta(days=3)

# TODO
default_ontology_handle = 'cache/ontologies/pato.json'
#if not os.path.isfile(ontology_handle):
#    ontology_handle = None

global default_ontology
default_ontology = None


class OntologyFactory():
    """
    Creates an ontology
    """

    # class variable - reuse the same object throughout
    test = 0
    
    def __init__(self, handle=None):
        """
        initializes based on an ontology name
        """
        self.handle = handle

    def create(self, handle=None):
        if handle == None:
            self.test = self.test+1
            logging.info("T: "+str(self.test))                
            global default_ontology
            if default_ontology == None:
                logging.info("Creating new instance of default ontology")
                default_ontology = create_ontology(default_ontology_handle)
            logging.info("Using default_ontology")                
            return default_ontology
        return create_ontology(handle)
    
#@cachier(stale_after=SHELF_LIFE)
def create_ontology(handle=None):
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
    elif handle.startswith("http:"):
        logging.info("Fetching from Web PURL: "+handle)
        encoded = hashlib.sha256(handle.encode()).hexdigest()
        #encoded = binascii.hexlify(bytes(handle, 'utf-8'))
        #base64.b64encode(bytes(handle, 'utf-8'))
        logging.info(" encoded: "+str(encoded))
        fn = '/tmp/'+encoded
        if not os.path.isfile(fn):
            cmd = ['owltools',handle,'-o','-f','json',fn]
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
