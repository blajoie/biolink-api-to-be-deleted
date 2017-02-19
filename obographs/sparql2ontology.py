"""
Reconsitutes an ontology from SPARQL queries over a remote SPARQL server
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from prefixcommons.curie_util import contract_uri
from functools import lru_cache
import percache
import networkx
from obographs.tuple_cache import store_object, fetch_object
from cachier import cachier
import datetime
import logging

SHELF_LIFE = datetime.timedelta(days=7)

# CACHE STRATEGY:
# by default, the cache is NOT persistent. Only single threaded clients should
# call a cached method with writecache=True.
# Note we are layering the in-memory cache over the persistent cache

cache = lru_cache(maxsize=None)
#cache = cachier(stale_after=SHELF_LIFE)


SUBCLASS_OF = 'subClassOf'

# TODO
# for now we assume ontobee
ontol_sources = {
    'go': "http://rdf.geneontology.org/sparql",
    '': "http://sparql.hegroup.org/sparql"
    }

    

def get_digraph(ont, relations=[], writecache=False):
    """
    Creates a basic graph object corresponding to a remote ontology
    """
    digraph = networkx.MultiDiGraph()
    for (s,p,o) in get_edges(ont):
        if relations==[] or p in relations:
            digraph.add_edge(o,s,pred=p)
    for (n,label) in fetchall_labels(ont):
        digraph.add_node(n, attr_dict={'label':label})
    return digraph


@cachier(stale_after=SHELF_LIFE)
def get_edges(ont):
    """
    Fetches all basic edges from a remote ontology
    """
    logging.info("QUERYING:"+ont)
    edges = [(c,SUBCLASS_OF, d) for (c,d) in fetchall_isa(ont)]
    edges += fetchall_svf(ont)
    return edges

def search(ont, searchterm):
    """
    Search for things using labels
    """
    namedGraph = get_named_graph(ont)
    query = """
    SELECT ?c ?l WHERE {{
    GRAPH <{g}>  {{
    ?c rdfs:label ?l
    FILTER regex(?l,'{s}','i')
    }}
    }}
    """.format(s=searchterm, g=namedGraph)
    bindings = run_sparql(query)
    return [(r['c']['value'],r['l']['value']) for r in bindings]

def get_terms_in_subset(ont, subset):
    """
    Find all nodes in a subset.

    We assume the oboInOwl encoding of subsets, and subset IDs are IRIs
    """
    namedGraph = get_named_graph(ont)

    # note subsets have an unusual encoding
    query = """
    prefix oboInOwl: <http://www.geneontology.org/formats/oboInOwl>
    SELECT ?c ? WHERE {{
    GRAPH <{g}>  {{
    ?c oboInOwl:inSubset ?s ;
       rdfs:label ?l
    FILTER regex(?s,'#{s}$','i')
    }}
    }}
    """.format(s=subset, g=namedGraph)
    bindings = run_sparql(query)
    return [(r['c']['value'],r['l']['value']) for r in bindings]


def run_sparql(q):
    # TODO: select based on ontology
    #sparql = SPARQLWrapper("http://rdf.geneontology.org/sparql")
    logging.info("Connecting to sparql endpoint...")
    sparql = SPARQLWrapper("http://sparql.hegroup.org/sparql")

    # TODO: iterate over large sets?
    full_q = q + ' LIMIT 250000'
    sparql.setQuery(q)
    sparql.setReturnFormat(JSON)
    results = sparql.query().convert()
    bindings = results['results']['bindings']
    for r in bindings:
        curiefy(r)
    return bindings


def curiefy(r):
    for (k,v) in r.items():
        if v['type'] == 'uri':
            curies = contract_uri(v['value'])
            if len(curies)>0:
                r[k]['value'] = curies[0]

def get_named_graph(ont):
    """
    Ontobee uses NGs such as http://purl.obolibrary.org/obo/merged/CL
    """

    namedGraph = 'http://purl.obolibrary.org/obo/merged/' + ont.upper()
    return namedGraph

def fetchall_isa(ont):
    namedGraph = get_named_graph(ont)
    queryBody = querybody_isa()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    bindings = run_sparql(query)
    return [(r['c']['value'],r['d']['value']) for r in bindings]

def fetchall_svf(ont):
    namedGraph = get_named_graph(ont)
    queryBody = querybody_svf()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    bindings = run_sparql(query)
    return [(r['c']['value'], r['p']['value'], r['d']['value']) for r in bindings]

#@cache
def old_fetchall_labels(ont,writecache=False):
    """
    fetch all rdfs:label assertions for an ontology
    """
    k=('fetchall_labels',ont)
    rows = fetch_object(k)
    if rows is not None:
        return rows
    namedGraph = get_named_graph(ont)
    queryBody = querybody_label()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    bindings = run_sparql(query)
    rows = [(r['c']['value'], r['l']['value']) for r in bindings]
    if writecache:
        store_object(k,rows)
    return rows

@cachier(stale_after=SHELF_LIFE)
def fetchall_labels(ont):
    """
    fetch all rdfs:label assertions for an ontology
    """
    logging.info("fetching rdfs:labels for: "+ont)
    namedGraph = get_named_graph(ont)
    queryBody = querybody_label()
    query = """
    SELECT * WHERE {{
    GRAPH <{g}>  {q}
    }}
    """.format(q=queryBody, g=namedGraph)
    bindings = run_sparql(query)
    rows = [(r['c']['value'], r['l']['value']) for r in bindings]
    return rows

def querybody_isa():
    return """
    { ?c rdfs:subClassOf ?d }
    FILTER (!isBlank(?c))
    FILTER (!isBlank(?d))
    """

def querybody_svf():
    return """
    { ?c rdfs:subClassOf [owl:onProperty ?p ; owl:someValuesFrom ?d ] }
    FILTER (!isBlank(?c))
    FILTER (!isBlank(?p))
    FILTER (!isBlank(?d))
    """

def querybody_label():
    return """
    { ?c rdfs:label ?l }
    """

## -- PERSISTENCE --


