import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from ontobio.golr.golr_associations import map2slim
from biolink.api.restplus import api
from scigraph.scigraph_util import SciGraph
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('bioentityset/slimmer', description='maps a set of entities to a slim')

parser = api.parser()
parser.add_argument('subject', action='append', help='Entity ids to be examined, e.g. NCBIGene:9342, NCBIGene:7227, NCBIGene:8131, NCBIGene:157570, NCBIGene:51164, NCBIGene:6689, NCBIGene:6387')
parser.add_argument('slim', action='append', help='Map objects up (slim) to a higher level category. Value can be ontology class ID (IMPLEMENTED) or subset ID (TODO)')

@ns.route('/<category>')
class EntitySetSlimmer(Resource):

    @api.expect(parser)
    def get(self, category):
        """
        Summarize a set of objects
        """
        args = parser.parse_args()
        logging.info("category is {}".format(category))
        slim = args.get('slim')
        del args['slim']
        subjects = args.get('subject')
        del args['subject']
        results = map2slim(subjects=subjects,
                           slim=slim,
                           object_category=category,
                           **args)
        # If there are no associations for the given ID, try other IDs.
        # Note the AmiGO instance does *not* support equivalent IDs
        assoc_count = 0
        for result in results:
            assoc_count += len(result['assocs'])
        if assoc_count == 0 and len(subjects) == 1:
            # Note that GO currently uses UniProt as primary ID for some sources: https://github.com/biolink/biolink-api/issues/66
            # https://github.com/monarch-initiative/dipper/issues/461
            # nota bene:
            # currently incomplete because code is not checking for the possibility of >1 subjects
            logging.info("Found no associations using {} - will try mapping to other IDs".format(subjects[0]))
            sg_dev = SciGraph(url='https://scigraph-data-dev.monarchinitiative.org/scigraph/')
            prots = sg_dev.gene_to_uniprot_proteins(subjects[0])
            if len(prots) > 0:
                results = map2slim(subjects=prots,
                                   slim=slim,
                                   object_category=category,
                                   **args)
        return results
