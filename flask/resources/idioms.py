# -*- coding: utf-8 -*-
import traceback
from bson import ObjectId
from flask_restplus import Namespace, reqparse, Resource

from core.response import (
    return_500_for_sever_error,
    return_401_for_no_auth,
    CustomeResponse,
)

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
from core.resource import token_checker

api = Namespace("idioms", description="Idioms related operations")


def get_only_idioms():
    return mongo.db.idioms.distinct("expression")


def get_only_public_idioms():
    return mongo.db.idioms.distinct("expression", gen_restrict_access_query())


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


def get_idioms(search_key=None, full_search=0, exact=0, only_public=False):
    try:
        query = {}
        if not only_public:
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
            user_info.id,
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
class Idioms(Resource, CustomeResponse):
    @api.doc("list_idioms")
    @api.expect(parser_search_idiom, parser_header)
    @token_checker
    @return_500_for_sever_error
    def get(self, **kwargs):
        only_public = (
            False if kwargs["auth_user"] and kwargs["auth_user"].is_admin() else False
        )
        args = parser_search_idiom.parse_args()
        result = get_idioms(
            search_key=args["search_key"],
            full_search=args["full_search"],
            exact=args["exact"],
            only_public=only_public,
        )
        return self.send(response_type="SUCCESS", result=result)

    @api.doc("add an idiom")
    @api.expect(parser_create, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        """Add an idiom"""
        if not kwargs["auth_user"].is_admin():
            return self.send(response_type="FORBIDDEN")

        args = parser_create.parse_args()
        result = upsert_idiom(args)
        status = "CREATED" if result else "FAIL"
        return self.send(response_type=status)

    @api.doc("delete an idiom")
    @api.expect(parser_delete, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, **kwargs):
        """Delete an idiom"""
        if not kwargs["auth_user"].is_admin():
            return self.send(response_type="FORBIDDEN")
        args = parser_delete.parse_args()
        result = delete_idiom(args)
        status = "NO_CONTENT" if result else "FAIL"
        return self.send(response_type=status)


def get_idiom_with_dictionary(idiom):
    return stringify_docs(mongo.db.idioms.find({"expression": idiom}))


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


parser_random = reqparse.RequestParser()
parser_random.add_argument("count", type=int, location="args")


@api.route("/random")
class PhrasalVerbs(Resource, CustomeResponse):
    @api.expect(parser_random)
    @return_500_for_sever_error
    def get(self):
        """List random phrasal verbs"""
        args = parser_random.parse_args()
        return self.send(
            response_type="SUCCESS", result=get_random_public_idioms(args["count"])
        )


@api.route("/<string:idiom>")
class Idiom(Resource, CustomeResponse):
    @api.expect(parser_header)
    @token_checker
    @return_500_for_sever_error
    def get(self, idiom, **kwargs):
        """Get a idiom verb"""
        if kwargs["auth_user"] and kwargs["auth_user"].is_admin():
            result = get_idiom_with_dictionary(idiom)
        else:
            result = get_idiom(idiom)
        if result:
            return self.send(response_type="SUCCESS", result=result)
        else:
            return self.send(response_type="NOT_FOUND")

    @api.expect(parser_header, parser_dictionary)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, idiom, **kwargs):
        if not kwargs["auth_user"].is_admin():
            return self.send(response_type="FORBIDDEN")

        args = parser_dictionary.parse_args()
        dictionary = {
            "definitions": args.definitions,
            "examples": args.examples,
            "sources": args.dictionaries,
            "uploaded_datetime": args.datetime,
        }
        if upsert_idiom_dictionary(idiom, dictionary):
            return self.send(response_type="SUCCESS")
        else:
            return self.send(response_type="FAIL")


@api.route("/likes")
class IdiomLikes(Resource, CustomeResponse):
    @api.doc("idiom likes")
    @api.expect(parser_get_idiom_like)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        args = parser_get_idiom_like.parse_args()
        result = {
            "count": get_idioms_like_count(args["idiom_id"]),
            "active": get_user_like_active_status(
                kwargs["auth_user"], args["idiom_id"]
            ),
        }
        return self.send(response_type="SUCCESS", result=result)

    @api.expect(parser_like_create, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        args = parser_like_create.parse_args()
        result = update_user_like_idiom(kwargs["auth_user"].id, args)
        if result:
            return self.send(response_type="SUCCESS")
        else:
            return self.send(response_type="FAIL")
