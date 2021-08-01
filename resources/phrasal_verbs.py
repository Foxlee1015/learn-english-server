# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
from bson import ObjectId
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.db import mongo
from core.resource import CustomResource, response, json_serializer, json_serializer_all_datetime_keys
from core.utils import check_if_only_int_numbers_exist, token_required, parse_given_str_datetime_or_current_datetime


api = Namespace('phrasal-verbs', description='Phrasal_verbs related operations')

def get_only_verbs():
    verbs = mongo.db.phrasal_verbs.distinct("verb");
    return verbs

def get_random_verbs(count):
    random_verbs = []
    try:
        for item in mongo.db.phrasal_verbs.aggregate([{"$sample": {"size":count}}]):
            random_verb = {}
            for key, value in item.items():
                if key == '_id': 
                    value = str(value)
                random_verb[key] = value
            random_verbs.append(random_verb)
        return random_verbs
    except:
        traceback.print_exc()
        return random_verbs


def get_phrasal_verb(verb):
    try:
        query = {
            'verb': verb
        }
        verb= mongo.db.phrasal_verbs.find_one(query)
        phrasal_verb = {}
        if verb:    
            for key, value in verb.items():
                if key == '_id': 
                    value = str(value)
                phrasal_verb[key] = value
            return phrasal_verb
    except:
        traceback.print_exc()
        return None

def get_phrasal_verbs(search_key=None, full_search=0):
    phrasal_verbs = []
    try:
        query = {}
        if search_key is not None:
            if full_search:
                query["$text"] = {"$search": search_key}
            else: # contains search key in verb field
                query["verb"] = {"$regex": search_key}

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
    except:
        traceback.print_exc()
        return phrasal_verbs

def upsert_phrasal_verbs(args):
    try:
        verb = args.verb
        particle = args.particle
        definitions = args.get("definitions") or []
        sentences = args.get("sentences") or []
        difficulty = args.get("difficulty") or 0
        is_public = args.get("is_public") or 0
        
        search_query = {"verb": verb}
        phrasal_verb_data = {}

        # old data
        items = mongo.db.phrasal_verbs.find(search_query)
        if items:
            for item in items:
                for key, value in item.items():
                    phrasal_verb_data[key] = value
        
        # new verb
        if phrasal_verb_data.get("verb") is None:
            phrasal_verb_data["verb"] = verb

        # first particle
        if phrasal_verb_data.get("particles") is None:
            phrasal_verb_data["particles"] = {}
        phrasal_verb_data["particles"][particle] = {
            "definitions": definitions,
            "sentences": sentences,
            "difficulty": difficulty,
            "is_public": is_public
        }
        
        mongo.db.phrasal_verbs.replace_one(search_query, phrasal_verb_data, upsert=True)
        return True

    except:
        traceback.print_exc()
        return False


def delete_phrasal_verbs(args):
    try:
        query = {}
        if args["_id"] is not None:
            query["_id"] = ObjectId(args["_id"])
            
        if args["verb"] is not None:
            query["verb"] = args["verb"]
        mongo.db.phrasal_verbs.delete_many(query)
        return True

    except:
        traceback.print_exc()
        return False


parser_create = reqparse.RequestParser()
parser_create.add_argument('verb', type=str, required=True, help='Verb')
parser_create.add_argument('particle', type=str, required=True, help='Particle(adverb or preposition')
parser_create.add_argument('definitions', type=str, help='Definitions', action='append')
parser_create.add_argument('sentences', type=str, help='Sentences', action='append')
parser_create.add_argument('difficulty', type=int, help='Learning level')
parser_create.add_argument('is_public', type=int, help='Public')

parser_search_verb = reqparse.RequestParser()
parser_search_verb.add_argument('only_verb', type=int, location="args", help="Return only verbs when 1")
parser_search_verb.add_argument('random_verb_count', type=int, location="args", help="Get random verbs")
parser_search_verb.add_argument('search_key', type=str, help='To search in verb field', location="args")
parser_search_verb.add_argument('full_search', type=int, help='Search in indexes(all fields) when 1', location="args")

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('_id', type=str, help='_id', location="args")
parser_delete.add_argument('verb', type=str, help='Verb', location="args")

@api.route('/')
class PhrasalVerbs(CustomResource):
    @api.doc('list of phrasal_verbs')
    @api.expect(parser_search_verb)
    def get(self):
        '''List all phrasal verbs'''
        try:
            result = []
            args = parser_search_verb.parse_args()
            if args['only_verb'] == 1:
                result = get_only_verbs()
            elif args['random_verb_count'] is not None:
                result = get_random_verbs(count=args['random_verb_count'])
            else:
                result = get_phrasal_verbs(search_key=args["search_key"], full_search=args["full_search"])
            
            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)
    
    @api.doc('add a phrasal verb')
    @api.expect(parser_create)
    def post(self):
        '''Add an phrasal verb'''
        try:
            args = parser_create.parse_args()
            result = upsert_phrasal_verbs(args)
            status = 201 if result else 400
            
            return self.send(status=status)
        except:
            return self.send(status=500)

    @api.doc('delete a phrasal verb')
    @api.expect(parser_delete)
    def delete(self):
        '''Delete an phrasal verb'''
        try:
            args = parser_delete.parse_args()
            result = delete_phrasal_verbs(args)
            status = 200 if result else 400
            
            return self.send(status=status)
        except:
            return self.send(status=500)

@api.route('/<string:verb>')
class PhrasalVerb(CustomResource):
    @api.doc('phrasal_verb')
    def get(self,verb):
        '''Get a phrasal verb'''
        try:
            result = get_phrasal_verb(verb)
            return self.send(status=200, result=result)
        except:
            return self.send(status=500)
