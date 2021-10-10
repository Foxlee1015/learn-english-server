# -*- coding: utf-8 -*-
from datetime import datetime
from dotenv import load_dotenv
import os
import subprocess
import traceback
from bson import ObjectId
from threading import Thread
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.resource import CustomResource
from core.utils import token_required
from core.mongo_db import (
    mongo,
    gen_restrict_access_query,
    gen_query,
    gen_random_docs_query,
    gen_not_empty_array_query,
    gen_match_and_query,
    stringify_docs,
    gen_collection_active_like_query,
    gen_user_active_like_query,
    gen_not_include_query,
    gen_return_fields_query,
    gen_include_query,
)

api = Namespace("phrasal-verbs", description="Phrasal_verbs related operations")


def get_all_unique_field_values(field):
    return mongo.db.phrasal_verbs.distinct(field)


def get_all_unique_field_public_values(field):
    return mongo.db.phrasal_verbs.distinct(field, gen_restrict_access_query())


def get_random_public_verbs(count):
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
        return stringify_docs(mongo.db.phrasal_verbs.aggregate(query))
    except:
        traceback.print_exc()
        return None


def get_random_verbs(count):
    try:
        match_and_filters = [
            gen_not_empty_array_query("definitions"),
            gen_not_empty_array_query("sentences"),
        ]
        query = [
            gen_match_and_query(match_and_filters),
            gen_random_docs_query(count),
        ]
        return stringify_docs(mongo.db.phrasal_verbs.aggregate(query))
    except:
        traceback.print_exc()
        return None


def get_phrasal_verbs(search_key=None, full_search=0, exact=0):
    try:
        query = gen_restrict_access_query()
        if search_key is not None:
            if full_search:
                query.update(gen_full_search_query(search_key, exact))
            else:
                query.update(gen_query("verb", search_key, exact))

            excludes = ["dictionaries", "is_public"]
            return_fields = gen_return_fields_query(excludes=excludes)
            return stringify_docs(mongo.db.phrasal_verbs.find(query, return_fields))
        else:
            return stringify_docs(mongo.db.phrasal_verbs.find(query))
    except:
        traceback.print_exc()
        return None


def gen_full_search_query(search_key, exact):
    return {
        "$or": [
            gen_query("verb", search_key, exact),
            gen_query("particle", search_key, exact),
            gen_query("definitions", search_key, exact),
            gen_query("sentences", search_key, exact),
        ]
    }


def gen_has_dictionary_query():
    return {
        "$or": [
            gen_include_query(field="merriam"),
            gen_include_query(field="cambridge"),
            gen_include_query(field="oxford"),
        ]
    }


def gen_phrasal_verb_search_query(verb, particle):
    if particle:
        return {"verb": verb, "particle": particle}
    return {"verb": verb}


def get_phrasal_verbs_with_dictionary(search_key=None, full_search=0, exact=0):
    try:
        query = {}
        if search_key is not None:
            if full_search:
                query.update(gen_full_search_query(search_key, exact))
            else:
                query.update(gen_query("verb", search_key, exact))
        return stringify_docs(mongo.db.phrasal_verbs.find(query))
    except:
        traceback.print_exc()
        return None


def upsert_phrasal_verbs(phrasal_verb):
    try:
        search_query = gen_phrasal_verb_search_query(
            phrasal_verb["verb"], phrasal_verb["particle"]
        )
        upsert_phrasal_verb = {"$set": phrasal_verb}
        rs = mongo.db.phrasal_verbs.update(
            search_query, upsert_phrasal_verb, upsert=True
        )
        return True

    except:
        traceback.print_exc()
        return False


def upsert_phrasal_verbs_dictionary(verb, particle, data):
    try:
        search_query = gen_phrasal_verb_search_query(verb, particle)
        upsert_dictionary = {"$set": {"dictionaries": data}}
        mongo.db.phrasal_verbs.update(search_query, upsert_dictionary, upsert=True)
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
    query = gen_collection_active_like_query(
        field_key="phrasalVerbId", field_value=phrasal_verb_id
    )
    return mongo.db.user_like_phrasal_verb.find(query).count()


def get_user_like_active_status(user_info, target):
    if user_info:
        query = gen_user_active_like_query(
            user_info["id"],
            field_key="phrasalVerbId",
            field_value=target,
        )
        if mongo.db.user_like_phrasal_verb.find_one(query):
            return 1
    return 0


def update_user_like_phrasal_verb(user_id, args):
    try:
        search_query = {
            "userId": user_id,
            "phrasalVerbId": args.phrasal_verb_id,
        }
        user_like = search_query.copy()
        user_like["active"] = args.like

        mongo.db.user_like_phrasal_verb.replace_one(
            search_query, user_like, upsert=True
        )
        return True
    except:
        traceback.print_exc()
        return None


def start_crawler():
    try:
        APP_ROOT = os.path.join(os.path.dirname(__file__), "..")
        dotenv_path = os.path.join(APP_ROOT, ".env")
        load_dotenv(dotenv_path)
        subprocess.call(["sh", os.getenv("CRAWLER")])

    except:
        traceback.print_exc()
        return None


def start_crawler_job():
    thread = Thread(target=start_crawler)
    thread.daemon = True
    thread.start()


parser_create = reqparse.RequestParser()
parser_create.add_argument("verb", type=str, required=True, help="Verb")
parser_create.add_argument(
    "particle", type=str, required=True, help="Particle(adverb or preposition"
)
parser_create.add_argument("definitions", type=str, help="Definitions", action="append")
parser_create.add_argument("sentences", type=str, help="Sentences", action="append")
parser_create.add_argument("difficulty", type=int, help="Learning level")
parser_create.add_argument("is_public", type=int, help="Public")

parser_search_verb = reqparse.RequestParser()
parser_search_verb.add_argument(
    "only_verb", type=int, location="args", help="Return only verbs when true value"
)
parser_search_verb.add_argument(
    "only_particle",
    type=int,
    location="args",
    help="Return only particles when true value",
)
parser_search_verb.add_argument(
    "random_count", type=int, location="args", help="Get random verbs"
)
parser_search_verb.add_argument(
    "search_key", type=str, help="To search in verb field", location="args"
)
parser_search_verb.add_argument(
    "full_search",
    type=int,
    help="Search in indexes(all fields) when 1",
    location="args",
)
parser_search_verb.add_argument(
    "exact", type=int, help="Search exact search key when 1", location="args"
)

parser_delete = reqparse.RequestParser()
parser_delete.add_argument("_id", type=str, help="_id", location="args")
parser_delete.add_argument("verb", type=str, help="Verb", location="args")
parser_delete.add_argument("particle", type=str, help="Particle", location="args")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, location="headers")

parser_get_phrasal_verb_like = reqparse.RequestParser()
parser_get_phrasal_verb_like.add_argument(
    "phrasal_verb_id", type=str, help="_id", required=True, location="args"
)
parser_get_phrasal_verb_like.add_argument("Authorization", type=str, location="headers")

parser_like_create = reqparse.RequestParser()
parser_like_create.add_argument(
    "phrasal_verb_id", type=str, required=True, help="Idiom id"
)
parser_like_create.add_argument("like", type=int, required=True, help="like when 1")


parser_dictionary = reqparse.RequestParser()
parser_dictionary.add_argument("particle", type=str, required=True)
parser_dictionary.add_argument("datetime", type=str, required=True)
parser_dictionary.add_argument(
    "dictionaries", type=str, required=True, help="Source dictionaries", action="append"
)
parser_dictionary.add_argument(
    "definitions", type=str, help="Definitions", action="append"
)
parser_dictionary.add_argument("examples", type=str, help="Examples", action="append")


@api.route("/")
class PhrasalVerbs(CustomResource):
    @api.doc("list of phrasal_verbs")
    @api.expect(parser_search_verb, parser_header)
    @token_required
    def get(self, **kwargs):
        """List all phrasal verbs"""
        try:
            admin = self.is_admin(kwargs["user_info"])
            args = parser_search_verb.parse_args()

            if args["only_verb"] or args["only_particle"]:
                field = "verb" if args["only_verb"] else "particle"
                if admin:
                    result = get_all_unique_field_values(field)
                else:
                    result = get_all_unique_field_public_values(field)

            elif args["random_count"] is not None:
                if admin:
                    result = get_random_verbs(count=args["random_count"])
                else:
                    result = get_random_public_verbs(count=args["random_count"])
            else:
                if admin:
                    result = get_phrasal_verbs_with_dictionary(
                        search_key=args["search_key"],
                        full_search=args["full_search"],
                        exact=args["exact"],
                    )
                else:
                    result = get_phrasal_verbs(
                        search_key=args["search_key"],
                        full_search=args["full_search"],
                        exact=args["exact"],
                    )
            if result is None:
                self.send(status=500)

            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("add a phrasal verb")
    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, **kwargs):
        """Add an phrasal verb"""
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            args = parser_create.parse_args()
            result = upsert_phrasal_verbs(args)

            if result:
                status = 201
                start_crawler_job()
            else:
                status = 400

            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete a phrasal verb")
    @api.expect(parser_delete, parser_header)
    @token_required
    def delete(self, **kwargs):
        """Delete an phrasal verb"""
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            args = parser_delete.parse_args()

            result = None  # delete_phrasal_verbs(args)
            status = 200 if result else 400

            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)


def get_phrasal_verb_with_dictionary(verb, particle):
    search_query = gen_phrasal_verb_search_query(verb, particle)
    return stringify_docs(mongo.db.phrasal_verbs.find(search_query))


parser_particle = reqparse.RequestParser()
parser_particle.add_argument("particle", type=str)


@api.route("/<string:verb>")
class PhrasalVerb(CustomResource):
    @api.doc("phrasal_verb")
    @api.expect(parser_header, parser_particle)
    @token_required
    def get(self, verb, **kwargs):
        """Get a phrasal verb"""
        try:
            args = parser_particle.parse_args()
            admin = self.is_admin(kwargs["user_info"])
            if admin:
                result = get_phrasal_verb_with_dictionary(verb, args["particle"])
            else:
                result = get_phrasal_verbs(search_key=verb, exact=1)

            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_dictionary, parser_header)
    @token_required
    def put(self, verb, **kwargs):
        try:
            if kwargs["user_info"] is None:
                return self.send(status=401)
            args = parser_dictionary.parse_args()
            dictionary = {
                "definitions": args.definitions,
                "examples": args.examples,
                "sources": args.dictionaries,
                "uploaded_datetime": args.datetime,
            }
            result = upsert_phrasal_verbs_dictionary(verb, args.particle, dictionary)
            if result:
                return self.send(status=200)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/likes")
class PhrasalVerbLikes(CustomResource):
    @api.doc("phrasal_verb")
    @api.expect(parser_get_phrasal_verb_like)
    @token_required
    def get(self, **kwargs):
        try:
            args = parser_get_phrasal_verb_like.parse_args()
            result = {
                "count": get_phrasal_verbs_like(args["phrasal_verb_id"]),
                "active": get_user_like_active_status(
                    kwargs["user_info"], args["phrasal_verb_id"]
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
            result = update_user_like_phrasal_verb(kwargs["user_info"]["id"], args)
            if result:
                return self.send(status=200)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)
