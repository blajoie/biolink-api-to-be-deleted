"""
@Deprecated
"""
import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api

import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('ontol/slimmer', description='Mapping to an ontology subset')

parser = api.parser()
#parser.add_argument('subject_taxon', help='SUBJECT TAXON id, e.g. NCBITaxon:9606. Includes inferred by default')

@ns.route('/<subset>')
class MapToSlimResource(Resource):


    @api.expect(parser)
    def get(self, subset):
        """
        TODO Maps to slim
        """
        args = parser.parse_args()

        return []

    

    
    

