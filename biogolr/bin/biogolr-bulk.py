#!/usr/bin/env python

"""
Bulk download

Type:

    qbiogorl -h

For instructions

Examples:

all human gene-phenotype associations:

    biogolr-bulk.py -s NCBITaxon:9606 -C gene phenotype



"""

import argparse
from biogolr.golr_associations import bulk_fetch
import networkx as nx
from networkx.algorithms.dag import ancestors, descendants
from networkx.drawing.nx_pydot import write_dot
from prefixcommons.curie_util import expand_uri
from obographs.slimmer import get_minimal_subgraph
import logging

def main():
    """
    Wrapper for OGR
    """

    parser = argparse.ArgumentParser(
        description='Command line interface to python-biogolr library'
        """

        Provides command line interface onto the biogolr python library, a high level 
        abstraction layer over Monarch and GO solr indices.
        """,
        formatter_class=argparse.RawTextHelpFormatter)

    parser.add_argument('-o', '--outfile', type=str, required=False,
                        help='Path to output file')
    parser.add_argument('-C', '--category', nargs=2, type=str, required=True,
                        help='Category')
    parser.add_argument('-s', '--species', type=str, required=True,
                        help='NCBITaxon ID')
    parser.add_argument('-S', '--slim', nargs='*', type=str, required=False,
                        help='Slim IDs')
    parser.add_argument('-L', '--limit', type=int, default=100000, required=False,
                        help='Limit on number of rows')
    parser.add_argument('-v', '--verbosity', default=0, action='count',
                        help='Increase output verbosity')

    parser.add_argument('ids',nargs='*')

    args = parser.parse_args()

    if args.verbosity >= 2:
        logging.basicConfig(level=logging.DEBUG)
    if args.verbosity == 1:
        logging.basicConfig(level=logging.INFO)
    logging.info("Welcome!")

    [subject_category, object_category] = args.category

    assocs = bulk_fetch(subject_category,
                        object_category,
                        args.species,
                        rows=args.limit,
                        slim=args.slim)
    
    for a in assocs:
        print("{}\t{}\t{}".format(a['subject'],
                                    a['relation'],
                                    ";".join(a['objects'])))

    
if __name__ == "__main__":
    main()
