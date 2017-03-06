"""
Mapping between obograph-JSON format and networkx
"""

import itertools
import re
import json

import networkx
import logging
from prefixcommons.curie_util import contract_uri

def contract_uri_wrap(uri):
    curies = contract_uri(uri)
    if len(curies) > 0:
        return curies[0]
    else:
        return uri

def add_obograph_digraph(og, digraph, node_type=None, predicates=None, **args):
    """
    Converts a single obograph to Digraph edges and adds to an existing networkx DiGraph
    """
    logging.info("NODES: {}".format(len(og['nodes'])))
    for n in og['nodes']:
        is_obsolete =  'is_obsolete' in n and n['is_obsolete'] == 'true'
        if is_obsolete:
            continue
        if node_type is not None and ('type' not in n or n['type'] != node_type):
            continue
        id = contract_uri_wrap(n['id'])
        digraph.add_node(id, attr_dict=n)
        if 'lbl' in n:
            digraph.node[id]['label'] = n['lbl']
    logging.info("EDGES: {}".format(len(og['edges'])))
    for e in og['edges']:
        sub = contract_uri_wrap(e['sub'])
        obj = contract_uri_wrap(e['obj'])
        pred = contract_uri_wrap(e['pred'])
        if pred == 'is_a':
            pred = 'subClassOf'
        if predicates is None or pred in predicates:
            digraph.add_edge(obj, sub, pred=pred)
    if 'equivalentNodesSets' in og:
        nslist = og['equivalentNodesSets']
        logging.info("CLIQUES: {}".format(len(nslist)))
        for ns in nslist:
            equivNodeIds = ns['nodeIds']
            for i in ns['nodeIds']:
                ix = contract_uri_wrap(i)
                for j in ns['nodeIds']:
                    if i != j:
                        jx = contract_uri_wrap(j)
                        digraph.add_edge(ix, jx, pred='equivalentTo')


def convert_json_string(obographstr, **args):
    """
    Return a networkx MultiDiGraph of the ontologies
    serialized as a json string
    """
    return convert_json_object(json.loads(obographstr), **args)

def convert_json_file(obographfile, **args):
    """
    Return a networkx MultiDiGraph of the ontologies
    serialized as a json string

    """
    f = open(obographfile, 'r')
    jsonstr = f.read()
    f.close()
    return convert_json_string(jsonstr, **args)

def convert_json_object(obographdoc, **args):
    """
    Return a networkx MultiDiGraph of the ontologies
    serialized as a json object

    """
    digraph = networkx.MultiDiGraph()
    for og in obographdoc['graphs']:
        add_obograph_digraph(og, digraph, **args)

    return digraph

