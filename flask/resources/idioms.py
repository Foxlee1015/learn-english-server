# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
from bson import ObjectId
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.resource import CustomResource
from core.utils import token_required
from core.mongo_db import mongo, gen_match_and_query, gen_random_docs_query, gen_not_empty_array_query, gen_restrict_access_query, gen_query, stringify_docs, gen_active_like_query

api = Namespace('idioms', description='Idioms related operations')


def get_only_idioms():
    return mongo.db.idioms.distinct("expression")


def get_random_idioms(count, admin=False):
    random_idioms = []
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
        random_idioms = stringify_docs(mongo.db.idioms.aggregate(query))
        return random_idioms
    except:
        traceback.print_exc()
        return random_idioms


def get_idioms(search_key=None, full_search=0, exact=0, admin=False):
    idioms = []
    try:
        query = gen_restrict_access_query(admin)
        if search_key is not None:
            if full_search:
                query["$or"] = [
                    gen_query("expression", search_key, exact),
                    gen_query("definitions", search_key, exact),
                    gen_query("sentences", search_key, exact),
                ]
            else:
                query.update(gen_query("expression", search_key, exact))
        idioms = stringify_docs(mongo.db.idioms.find(query))
        return idioms
    except:
        traceback.print_exc()
        return idioms

def add_idiom(args):
    try:
        idiom_data = {
            "expression": args.expression,
            "definitions": args.get("definitions") or [],
            "sentences": args.get("sentences") or [],
            "difficulty": args.get("difficulty") or 0,
            "is_public": args.get("is_public") or 0
        }
        mongo.db.idioms.insert_one(idiom_data)
        return True
    except:
        traceback.print_exc()
        return False


def delete_idiom(args):
    try:
        query = {}
        if args["_id"] is not None:
            query["_id"] = ObjectId(args["_id"])
            
        if args["expression"] is not None:
            query["expression"] = args["expression"]
            
        mongo.db.idioms.delete_many(query)
        return True
    except:
        traceback.print_exc()
        return False

def get_idioms_like_count(idiom_id):
    query = gen_active_like_query("idiomId", idiom_id)
    return mongo.db.user_like_idiom.find(query).count()

def check_user_like(idiom_id, user_id):
    query = gen_active_like_query("idiomId", idiom_id, user_id=user_id)
    return mongo.db.user_like_idiom.find_one(query)

def update_user_like_idiom(args):
    try:
        search_query = {
            "userId": args.user_id,
            "idiomId": args.idiom_id,
        }
        user_like = search_query.copy()
        user_like["active"] = args.like
        mongo.db.user_like_idiom.replace_one(search_query, user_like, upsert=True)
        return True
    except:
        traceback.print_exc()
        return None

parser_create = reqparse.RequestParser()
parser_create.add_argument('expression', type=str, required=True, help='Expression')
parser_create.add_argument('definitions', type=str, help='Definitions', action='append')
parser_create.add_argument('sentences', type=str, help='Sentences', action='append')
parser_create.add_argument('difficulty', type=int, help='Learning level')
parser_create.add_argument('is_public', type=int, help='Public')

parser_search_idiom = reqparse.RequestParser()
parser_search_idiom.add_argument('only_idiom', type=int, location="args", help="Return only idioms when 1")
parser_search_idiom.add_argument('search_key', type=str, help='To search in idiom field', location="args")
parser_search_idiom.add_argument('full_search', type=int, help='Search in indexes(all fields) when 1', location="args")
parser_search_idiom.add_argument('exact', type=int, help='Search exact search key when 1', location="args")
parser_search_idiom.add_argument('random_count', type=int, location="args", help="Get random verbs")


parser_delete = reqparse.RequestParser()
parser_delete.add_argument('_id', type=str, help='_id', location="args")
parser_delete.add_argument('expression', type=str, help='Expression', location="args")

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, location='headers')

parser_get_idiom_like = reqparse.RequestParser()
parser_get_idiom_like.add_argument('idiom_id', type=str, help='_id', required=True, location="args")
parser_get_idiom_like.add_argument('Authorization', type=str, location='headers')


parser_like_create = reqparse.RequestParser()
parser_like_create.add_argument('idiom_id', type=str, required=True, help='Idiom id')
parser_like_create.add_argument('like', type=int, required=True, help='like when 1')


@api.route('/')
class Idioms(CustomResource):
    @api.doc('list_idioms')
    @api.expect(parser_search_idiom, parser_header)
    @token_required
    def get(self, **kwargs):
        '''List all idioms'''
        try:
            result = []
            admin = self.is_admin(kwargs["user_info"])

            args = parser_search_idiom.parse_args()
            if args['only_idiom'] == 1:
                result = get_only_idioms()
            elif args['random_count'] is not None:
                result = get_random_idioms(count=args['random_count'], admin=admin)
            else:
                result = get_idioms(
                    search_key=args["search_key"], full_search=args["full_search"], 
                    exact=args["exact"], admin=admin)
            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('add an idiom')
    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, **kwargs):
        '''Add an idiom'''
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)

            args = parser_create.parse_args()
            result = add_idiom(args)
            status = 201 if result else 400
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('delete an idiom')
    @api.expect(parser_delete, parser_header)
    @token_required
    def delete(self, **kwargs):
        '''Delete an idiom'''
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            args = parser_delete.parse_args()
            result = delete_idiom(args)
            status = 200 if result else 400        
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route('/likes')
class IdiomLikes(CustomResource):
    @api.doc('idiom likes')
    @api.expect(parser_get_idiom_like)
    @token_required
    def get(self, **kwargs):
        try:
            result = {
                "count": 0,
                "active" : 0
            }
            args = parser_get_idiom_like.parse_args()
            result["count"] = get_idioms_like_count(args["idiom_id"])
            if kwargs["user_info"] is not None:
                if check_user_like(args["idiom_id"],kwargs["user_info"]["id"]):
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
            result = update_user_like_idiom(args)
            if result:
                return self.send(status=200)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)