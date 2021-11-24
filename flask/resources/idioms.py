# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
from bson import ObjectId
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.resource import CustomResource
from core.utils import token_required
from core.mongo_db import (
    mongo,
    gen_match_and_query,
    gen_random_docs_query,
    gen_not_empty_array_query,
    gen_restrict_access_query,
    gen_query,
    stringify_docs,
    gen_collection_active_like_query,
    gen_user_active_like_query,
    gen_return_fields_query,
)

api = Namespace("idioms", description="Idioms related operations")


def get_only_idioms():
    return mongo.db.idioms.distinct("expression")


def get_only_public_idioms():
    return mongo.db.idioms.distinct("expression", gen_restrict_access_query())


def get_random_idioms(count):
    try:
        match_and_filters = [
            gen_not_empty_array_query("definitions"),
            gen_not_empty_array_query("sentences"),
        ]
        query = [
            gen_match_and_query(match_and_filters),
            gen_random_docs_query(count),
        ]
        return stringify_docs(mongo.db.idioms.aggregate(query))
    except:
        traceback.print_exc()
        return None


def get_random_public_idioms(count):
    try:
        match_and_filters = [
            gen_not_empty_array_query("definitions"),
            gen_not_empty_array_query("sentences"),
            gen_restrict_access_query(),
        ]
        query = [
            gen_match_and_query(match_and_filters),
            gen_random_docs_query(count),
        ]
        return stringify_docs(mongo.db.idioms.aggregate(query))
    except:
        traceback.print_exc()
        return None


def get_idioms(search_key=None, full_search=0, exact=0, admin=False):
    try:
        query = {}
        if not admin:
            query = gen_restrict_access_query()
        if search_key is not None:
            if full_search:
                query["$or"] = [
                    gen_query("expression", search_key, exact),
                    gen_query("definitions", search_key, exact),
                    gen_query("sentences", search_key, exact),
                ]
            else:
                query.update(gen_query("expression", search_key, exact))
        return stringify_docs(mongo.db.idioms.find(query))
    except:
        traceback.print_exc()
        return None


def add_idiom(args):
    try:
        idiom_data = {
            "expression": args.expression,
            "definitions": args.get("definitions") or [],
            "sentences": args.get("sentences") or [],
            "difficulty": args.get("difficulty") or 0,
            "is_public": args.get("is_public") or 0,
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
    query = gen_collection_active_like_query(field_key="idiomId", field_value=idiom_id)
    return mongo.db.user_like_idiom.find(query).count()


def get_user_like_active_status(user_info, target):
    if user_info:
        query = gen_user_active_like_query(
            user_info["id"],
            field_key="idiomId",
            field_value=target,
        )
        if mongo.db.user_like_idiom.find_one(query):
            return 1
    return 0


def update_user_like_idiom(user_id, args):
    try:
        search_query = {
            "userId": user_id,
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
parser_create.add_argument("expression", type=str, required=True, help="Expression")
parser_create.add_argument("definitions", type=str, help="Definitions", action="append")
parser_create.add_argument("sentences", type=str, help="Sentences", action="append")
parser_create.add_argument("difficulty", type=int, help="Learning level")
parser_create.add_argument("is_public", type=int, help="Public")

parser_search_idiom = reqparse.RequestParser()
parser_search_idiom.add_argument(
    "only_idiom", type=int, location="args", help="Return only idioms when true value"
)
parser_search_idiom.add_argument(
    "search_key", type=str, help="To search in idiom field", location="args"
)
parser_search_idiom.add_argument(
    "full_search",
    type=int,
    help="Search in indexes(all fields) when 1",
    location="args",
)
parser_search_idiom.add_argument(
    "exact", type=int, help="Search exact search key when 1", location="args"
)
parser_search_idiom.add_argument(
    "random_count", type=int, location="args", help="Get random verbs"
)


parser_delete = reqparse.RequestParser()
parser_delete.add_argument("_id", type=str, help="_id", location="args")
parser_delete.add_argument("expression", type=str, help="Expression", location="args")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, location="headers")

parser_get_idiom_like = reqparse.RequestParser()
parser_get_idiom_like.add_argument(
    "idiom_id", type=str, help="_id", required=True, location="args"
)
parser_get_idiom_like.add_argument("Authorization", type=str, location="headers")


parser_like_create = reqparse.RequestParser()
parser_like_create.add_argument("idiom_id", type=str, required=True, help="Idiom id")
parser_like_create.add_argument("like", type=int, required=True, help="like when 1")

parser_dictionary = reqparse.RequestParser()
parser_dictionary.add_argument("datetime", type=str, required=True)
parser_dictionary.add_argument(
    "dictionaries", type=str, help="Source dictionaries", action="append"
)
parser_dictionary.add_argument(
    "definitions", type=str, help="Definitions", action="append"
)
parser_dictionary.add_argument("examples", type=str, help="Examples", action="append")


def upsert_idiom(idiom_info):
    try:
        upsert_idiom = {"$set": idiom_info}
        rs = mongo.db.idioms.update(
            {"expression": idiom_info["expression"]}, upsert_idiom, upsert=True
        )
        print(rs)
        return True

    except:
        traceback.print_exc()
        return False


@api.route("/")
class Idioms(CustomResource):
    @api.doc("list_idioms")
    @api.expect(parser_search_idiom, parser_header)
    @token_required
    def get(self, **kwargs):
        """List all idioms"""
        try:
            admin = self.is_admin(kwargs["user_info"])

            args = parser_search_idiom.parse_args()
            if args["only_idiom"]:
                if admin:
                    result = get_only_idioms()
                else:
                    result = get_only_public_idioms()
            elif args["random_count"] is not None:
                if admin:
                    result = get_random_idioms(count=args["random_count"])
                else:
                    result = get_random_public_idioms(count=args["random_count"])
            else:
                result = get_idioms(
                    search_key=args["search_key"],
                    full_search=args["full_search"],
                    exact=args["exact"],
                    admin=admin,
                )
            if result is None:
                self.send(status=500)
            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("add an idiom")
    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, **kwargs):
        """Add an idiom"""
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)

            args = parser_create.parse_args()
            print(args)
            result = upsert_idiom(args)
            status = 201 if result else 400
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete an idiom")
    @api.expect(parser_delete, parser_header)
    @token_required
    def delete(self, **kwargs):
        """Delete an idiom"""
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


def get_idiom_with_dictionary(idiom):
    try:
        return stringify_docs(mongo.db.idioms.find({"expression": idiom}))
    except:
        traceback.print_exc()
        return None


def get_idiom(idiom):
    try:
        query = gen_restrict_access_query()
        query.update({"expression": idiom})
        return_fields = gen_return_fields_query(excludes=["dictionaries", "is_public"])
        return stringify_docs(mongo.db.idioms.find(query, return_fields))
    except:
        traceback.print_exc()
        return None


def upsert_idiom_dictionary(idiom, data):
    try:
        upsert_dictionary = {"$set": {"dictionaries": data}}
        mongo.db.idioms.update({"expression": idiom}, upsert_dictionary, upsert=True)
        return True

    except:
        traceback.print_exc()
        return False


@api.route("/<string:idiom>")
class Idiom(CustomResource):
    @api.expect(parser_header)
    @token_required
    def get(self, idiom, **kwargs):
        """Get a idiom verb"""
        try:
            if self.is_admin(kwargs["user_info"]):
                result = get_idiom_with_dictionary(idiom)
            else:
                result = get_idiom(idiom)
            status = 200 if result else 404
            return self.send(status=status, result=result)

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_header, parser_dictionary)
    @token_required
    def put(self, idiom, **kwargs):
        try:
            print(idiom)
            if kwargs["user_info"] is None:
                return self.send(status=401)
            args = parser_dictionary.parse_args()
            dictionary = {
                "definitions": args.definitions,
                "examples": args.examples,
                "sources": args.dictionaries,
                "uploaded_datetime": args.datetime,
            }
            result = upsert_idiom_dictionary(idiom, dictionary)
            status = 200 if result else 404
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/likes")
class IdiomLikes(CustomResource):
    @api.doc("idiom likes")
    @api.expect(parser_get_idiom_like)
    @token_required
    def get(self, **kwargs):
        try:
            args = parser_get_idiom_like.parse_args()
            result = {
                "count": get_idioms_like_count(args["idiom_id"]),
                "active": get_user_like_active_status(
                    kwargs["user_info"], args["idiom_id"]
                ),
            }
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
            result = update_user_like_idiom(kwargs["user_info"]["id"], args)
            if result:
                return self.send(status=200)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)
