from nsweb.api import bp
from flask import jsonify, request
from nsweb.api.schemas import (StudySchema,
                               DecodingSchema, GeneSchema)
from nsweb.models.studies import Study
from nsweb.models.decodings import Decoding
from nsweb.models.genes import Gene
from nsweb.controllers import decode
from nsweb.core import cache
import re


def make_cache_key():
    ''' Replace default cache key prefix with a string that also includes
    query arguments. '''
    return request.path + request.query_string.decode('utf-8')


@bp.route('/studies/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_studies():
    """
    Retrieve study data
    ---
    tags:
        - studies
    responses:
        200:
            description: Study data
        default:
            description: No studies found
    parameters:
        - in: query
          name: limit
          description: Maximum number of studies to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: search
          description: Search study fields (title, authors, journal, and year)
          type: string
          required: false
        - in: query
          name: pmid
          description: PubMed ID(s) of one or more studies
          required: false
          collectionFormat: csv
          type: array
          items:
            type: integer
    """
    DEFAULT_LIMIT = 25
    MAX_LIMIT = 100
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    limit = min(limit, MAX_LIMIT)
    page = int(request.args.get('page', 1))

    studies = Study.query

    if 'pmid' in request.args or 'id' in request.args:
        ids = request.args.get('id', None)
        ids = request.args.get('pmid', ids)
        ids = re.split('[\s,]+', ids.strip(' ,'))
        studies = studies.filter(Study.pmid.in_([int(x) for x in ids]))

    if 'search' in request.args and len(request.args['search']) > 1:
        search = '%{}%'.format(request.args['search'])
        studies = studies.filter(Study.title.like(search) |
                                 Study.authors.like(search) |
                                 Study.journal.like(search) |
                                 Study.year.like(search))

    studies = studies.paginate(page, limit, False).items
    schema = StudySchema(many=True)
    return jsonify(data=schema.dump(studies).data)


@bp.route('/decode/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_decoding():
    """
    Retrieve decoding data for a single image
    ---
    tags:
        - decode
    responses:
        200:
            description: Decoding data
        default:
            description: Decoding not found
    parameters:
        - in: query
          name: uuid
          description: UUID of the decoding
          required: false
          type: string
        - in: query
          name: image
          description: ID of image to decode
          type: integer
          required: false
        - in: query
          name: neurovault
          description: NeuroVault ID of image to decode
          type: integer
          required: false
        - in: query
          name: url
          description: URL of Nifti image to decode
          type: string
          required: false
    """
    dec = Decoding.query.filter_by(display=1)

    if 'uuid' in request.args:
        dec = dec.filter_by(uuid=request.args['uuid']).first()

    elif 'image' in request.args:
        dec = decode.decode_analysis_image(request.args['image'])

    elif 'neurovault' in request.args:
        dec_id = decode.decode_neurovault(request.args['neurovault'],
                                          render=False)
        dec = dec.filter_by(uuid=dec_id).first()

    elif 'url' in request.args:
        dec_id = decode.decode_url(request.args['url'], render=False)
        dec = dec.filter_by(uuid=dec_id).first()

    schema = DecodingSchema()
    return jsonify(data=schema.dump(dec).data)


@bp.route('/genes/')
@cache.cached(timeout=3600, key_prefix=make_cache_key)
def get_genes():
    """
    Retrieve gene data
    ---
    tags:
        - genes
    responses:
        200:
            description: Gene information
        default:
            description: No genes found
    parameters:
        - in: query
          name: limit
          description: Maximum number of genes to retrieve (default = 25; max = 100)
          type: integer
          required: false
        - in: query
          name: page
          description: Page number
          type: integer
          required: false
        - in: query
          name: symbol
          description: Gene symbol
          type: array
          required: false
          collectionFormat: csv
          items:
            type: string
        - in: query
          name: id
          description: Gene ID(s)
          required: false
          collectionFormat: csv
          type: array
          items:
            type: integer
    """
    DEFAULT_LIMIT = 25
    MAX_LIMIT = 100
    limit = int(request.args.get('limit', DEFAULT_LIMIT))
    limit = min(limit, MAX_LIMIT)
    page = int(request.args.get('page', 1))

    genes = Gene.query

    if 'id' in request.args:
        ids = re.split('[\s,]+', request.args['id'].strip(' ,'))
        genes = genes.filter(Gene.id.in_([int(x) for x in ids]))

    if 'symbol' in request.args:
        symbols = re.split('[\s,]+', request.args['symbol'].strip(' ,'))
        genes = genes.filter(Gene.symbol.in_(symbols))

    genes = genes.paginate(page, limit, False).items
    schema = GeneSchema(many=True)
    return jsonify(data=schema.dump(genes).data)
