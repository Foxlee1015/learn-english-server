# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.db import mongo
from core.resource import CustomResource, response, json_serializer, json_serializer_all_datetime_keys
from core.utils import check_if_only_int_numbers_exist, token_required, parse_given_str_datetime_or_current_datetime


api = Namespace('phrasal-verbs', description='Phrasal_verbs related operations')

def get_only_verbs():
    verbs = set()
    for item in mongo.db.phrasal_verbs.find():
        verbs.add(item["verb"])
    print('zxvzvxcv', verbs)
    return list(verbs)

def get_phrasal_verbs(verb=None, particle=None):
    query = {}
    if verb is not None:
        query["verb"] = verb
    if particle is not None:
        query["particle"] = particle

    phrasal_verbs = []
    for item in mongo.db.phrasal_verbs.find(query):
        phrasal_verb = {}
        for key, value in item.items():
            if key == '_id': 
                value = str(value)
            if key == 'created_time':
                value = json_serializer(value)
            
            phrasal_verb[key] = value
        phrasal_verbs.append(phrasal_verb)
    
    return phrasal_verbs

def add_phrasal_verbs(args):
    try:
        print(args)
        mongo.db.phrasal_verbs.insert_one(args)
        return True
    except:
        return False

parser_create = reqparse.RequestParser()
parser_create.add_argument('verb', type=str, required=True, help='Verb')
parser_create.add_argument('particle', type=str, required=True, help='Particle(adverb or preposition')
parser_create.add_argument('definitions', type=str, help='Definitions', action='append')
parser_create.add_argument('sentences', type=str, help='Sentences', action='append')
parser_create.add_argument('level', type=int, help='Learning level')

parser_search_verb = reqparse.RequestParser()
parser_search_verb.add_argument('only_verb', type=int, location="args")

parser_search = reqparse.RequestParser()
parser_search.add_argument('particle', type=str, help='Particle(adverb or preposition', location="args")


@api.route('/')
class PhrasalVerbs(CustomResource):
    @api.doc('list of phrasal_verbs')
    @api.expect(parser_search_verb)
    @api.response(203, 'Phrasal verb does not exist')
    def get(self):
        '''List all phrasal verbs'''
        args = parser_search_verb.parse_args()
        if args['only_verb'] == 1:
            result = get_only_verbs()
        else:
            result = get_phrasal_verbs()
        status = 200 if result else 203
        return self.send(status=status, result=result)

    
    @api.doc('add a phrasal verb')
    @api.expect(parser_create)
    @api.response(409, 'Duplicate phrasal verb')
    def post(self):
        '''Add an phrasal verb'''
        
        args = parser_create.parse_args()
        result = add_phrasal_verbs(args)
        status = 200 if result else 400
        
        return self.send(status=status)


@api.route('/<string:verb>')
class PhrasalVerb(CustomResource):
    @api.doc('phrasal_verb')
    @api.response(203, 'Phrasal verb does not exist')
    @api.expect(parser_search)
    def get(self,verb):
        '''Get a phrasal verb'''
        args = parser_search.parse_args()     
        result = get_phrasal_verbs(verb=verb, particle=args["particle"])
        status = 200 if result else 203
        return self.send(status=status, result=result)
