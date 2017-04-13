import logging

from flask import request
from flask_restplus import Resource
from biolink.datamodel.serializers import association
from biolink.api.restplus import api
import pysolr

log = logging.getLogger(__name__)

ns = api.namespace('nlp/annotate', description='annotate text using named entities')

parser = api.parser()
parser.add_argument('category', action='append', help='E.g. phenotype')

@ns.route('/<text>')
class Annotate(Resource):

    @api.expect(parser)
    @api.marshal_list_with(association)

    @api.expect(parser)
    @api.marshal_list_with(association)
    def get(self, text):
        """
        Not yet implemented. For now using scigraph annotator directly
        """
        args = parser.parse_args()

        return []


    
    

