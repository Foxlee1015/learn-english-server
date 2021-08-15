# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
from bson import ObjectId
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.resource import CustomResource
from core.utils import token_required
from core.mongo_db import mongo, gen_restrict_access_query, gen_query, gen_random_docs_query, gen_not_empty_array_query, gen_match_and_query, stringify_docs, gen_active_like_query

api = Namespace('phrasal-verbs', description='Phrasal_verbs related operations')

def get_unique_values(field):
    verbs = mongo.db.phrasal_verbs.distinct(field)
    return verbs

def get_random_verbs(count, admin=False):
    random_verbs = []
    try:
        match_and_filters = [
            gen_not_empty_array_query("definitions"),
            gen_not_empty_array_query("sentences"),
            gen_restrict_access_query(admin)
        ]

        query = [
            gen_match_and_query(match_and_filters),
            gen_random_docs_query(count),
        ]
        random_verbs = stringify_docs(mongo.db.phrasal_verbs.aggregate(query))
        return random_verbs
    except:
        traceback.print_exc()
        return random_verbs


def get_phrasal_verbs(search_key=None, full_search=0, exact=0, admin=False):
    phrasal_verbs = []
    try:
        query = gen_restrict_access_query(admin)
        if search_key is not None:
            if full_search:
                query["$or"] = [
                    gen_query("verb", search_key, exact),
                    gen_query("particle", search_key, exact),
                    gen_query("definitions", search_key, exact),
                    gen_query("sentences", search_key, exact),
                ]
            else:
                query.update(gen_query("verb", search_key, exact))
        phrasal_verbs = stringify_docs(mongo.db.phrasal_verbs.find(query))
        return phrasal_verbs
    except:
        traceback.print_exc()
        return phrasal_verbs


def upsert_phrasal_verbs(args):
    try:
        search_query = {
            "verb": args.verb,
            "particle": args.particle,
        }
        
        phrasal_verb_data = {
            "verb": args.verb,
            "particle": args.particle,
            "definitions": args.get("definitions") or [],
            "sentences": args.get("sentences") or [],
            "difficulty": args.get("difficulty") or 0,
            "is_public": args.get("is_public") or 0
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
        
        if args["particle"] is not None:
            query["particle"] = args["verb"]
        mongo.db.phrasal_verbs.delete_many(query)
        return True

    except:
        traceback.print_exc()
        return False

def get_phrasal_verbs_like(phrasal_verb_id):
    query = gen_active_like_query("phrasalVerbId", phrasal_verb_id)
    return mongo.db.user_like_phrasal_verb.find(query).count()


def check_user_like(phrasal_verb_id, user_id):
    query = gen_active_like_query("phrasalVerbId", phrasal_verb_id, user_id=user_id)
    return mongo.db.user_like_phrasal_verb.find_one(query)


def update_user_like_phrasal_verb(args):
    try:
        search_query = {
            "userId": args.user_id,
            "phrasalVerbId": args.phrasal_verb_id,
        }
        user_like = search_query.copy()
        user_like["active"] = args.like
    
        mongo.db.user_like_phrasal_verb.replace_one(search_query, user_like, upsert=True)
        return True
    except:
        traceback.print_exc()
        return None
        
parser_create = reqparse.RequestParser()
parser_create.add_argument('verb', type=str, required=True, help='Verb')
parser_create.add_argument('particle', type=str, required=True, help='Particle(adverb or preposition')
parser_create.add_argument('definitions', type=str, help='Definitions', action='append')
parser_create.add_argument('sentences', type=str, help='Sentences', action='append')
parser_create.add_argument('difficulty', type=int, help='Learning level')
parser_create.add_argument('is_public', type=int, help='Public')

parser_search_verb = reqparse.RequestParser()
parser_search_verb.add_argument('only_verb', type=int, location="args", help="Return only verbs when 1")
parser_search_verb.add_argument('only_particle', type=int, location="args", help="Return only particles when 1")
parser_search_verb.add_argument('random_count', type=int, location="args", help="Get random verbs")
parser_search_verb.add_argument('search_key', type=str, help='To search in verb field', location="args")
parser_search_verb.add_argument('full_search', type=int, help='Search in indexes(all fields) when 1', location="args")
parser_search_verb.add_argument('exact', type=int, help='Search exact search key when 1', location="args")

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('_id', type=str, help='_id', location="args")
parser_delete.add_argument('verb', type=str, help='Verb', location="args")
parser_delete.add_argument('particle', type=str, help='Particle', location="args")

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, location='headers')

parser_get_phrasal_verb_like = reqparse.RequestParser()
parser_get_phrasal_verb_like.add_argument('phrasal_verb_id', type=str, help='_id', required=True, location="args")
parser_get_phrasal_verb_like.add_argument('Authorization', type=str, location='headers')

parser_like_create = reqparse.RequestParser()
parser_like_create.add_argument('phrasal_verb_id', type=str, required=True, help='Idiom id')
parser_like_create.add_argument('like', type=int, required=True, help='like when 1')


@api.route('/')
class PhrasalVerbs(CustomResource):
    @api.doc('list of phrasal_verbs')
    @api.expect(parser_search_verb, parser_header)
    @token_required
    def get(self, **kwargs):
        '''List all phrasal verbs'''
        try:
            result = []
            admin = self.is_admin(kwargs["user_info"])

            args = parser_search_verb.parse_args()
            if args['only_verb'] == 1:
                result = get_unique_values('verb')
            elif args['only_particle'] == 1:
                result = get_unique_values('particle')
            elif args['random_count'] is not None:
                result = get_random_verbs(count=args['random_count'], admin=admin)
            else:
                result = get_phrasal_verbs(
                    search_key=args["search_key"], full_search=args["full_search"], 
                    exact=args["exact"], admin=admin)
            
            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)
    
    @api.doc('add a phrasal verb')
    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, **kwargs):
        '''Add an phrasal verb'''
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            args = parser_create.parse_args()
            result = upsert_phrasal_verbs(args)
            status = 201 if result else 400
            
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('delete a phrasal verb')
    @api.expect(parser_delete, parser_header)
    @token_required
    def delete(self, **kwargs):
        '''Delete an phrasal verb'''
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)

            args = parser_delete.parse_args()
            result = delete_phrasal_verbs(args)
            status = 200 if result else 400
            
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)

@api.route('/<string:verb>')
class PhrasalVerb(CustomResource):
    @api.doc('phrasal_verb')
    def get(self,verb):
        '''Get a phrasal verb'''
        try:
            result = get_phrasal_verbs(search_key=verb)

            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)

@api.route('/likes')
class PhrasalVerbLikes(CustomResource):
    @api.doc('phrasal_verb')
    @api.expect(parser_get_phrasal_verb_like)
    @token_required
    def get(self, **kwargs):
        try:
            result = {
                "count": 0,
                "active" : 0
            }
            args = parser_get_phrasal_verb_like.parse_args()
            result["count"] = get_phrasal_verbs_like(args["phrasal_verb_id"])
            if kwargs["user_info"] is not None:
                if check_user_like(args["phrasal_verb_id"],kwargs["user_info"]["id"]):
                    result["active"] = 1

            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)
    
    @api.expect(parser_like_create, parser_header)
    @token_required
    def post(self, **kwargs):
        try:
            if kwargs["user_info"] is None:
                return self.send(status=401)
            args = parser_like_create.parse_args()
            args["user_id"] = kwargs["user_info"]["id"]
            result = update_user_like_phrasal_verb(args)
            if result:
                return self.send(status=200)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)