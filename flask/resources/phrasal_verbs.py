# -*- coding: utf-8 -*-
from dotenv import load_dotenv
import os
import traceback
from bson import ObjectId
from threading import Thread
from flask_restplus import Namespace, reqparse, Resource

from core.resource import token_checker
from core.response import (
    CustomeResponse,
    return_500_for_sever_error,
    return_401_for_no_auth,
)
from core.utils import execute_command_ssh
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
    gen_return_fields_query,
    gen_include_query,
)

api = Namespace("phrasal-verbs", description="Phrasal_verbs related operations")


def get_random_public_verbs(count):
    count = 1 if not count else count
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


def get_phrasal_verb(phrasal_verb):
    try:
        query = gen_restrict_access_query()
        query.update(gen_phrasal_verb_search_query(phrasal_verb))
        return_fields = gen_return_fields_query(excludes=["dictionaries", "is_public"])
        return stringify_docs(mongo.db.phrasal_verbs.find(query, return_fields))
    except:
        traceback.print_exc()
        return None


def get_verbs_from_phrasal_verbs(
    search_key=None, full_search=0, exact=0, only_public=True
):
    try:
        query = {}
        return_fields = None
        if only_public:
            query = gen_restrict_access_query()
            return_fields = gen_return_fields_query(
                includes=["verb", "particle", "phrasal_verb"]
            )
        if search_key is not None:
            if full_search:
                query.update(gen_full_search_query(search_key, exact))
            else:
                query.update(gen_query("verb", search_key, exact))
        return stringify_docs(mongo.db.phrasal_verbs.find(query, return_fields))
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


def gen_phrasal_verb_search_query(phrasal_verb):
    result = None
    verb, particle = get_verb_particle_from_phrasal_verb(phrasal_verb)
    if verb:
        result = {"verb": verb}
    if particle:
        result["particle"] = particle
    return result


def upsert_phrasal_verb(phrasal_verb_info):
    try:
        verb = phrasal_verb_info["verb"]
        particle = phrasal_verb_info["particle"]
        search_query = {"verb": verb, "particle": particle}
        phrasal_verb_info.update({"phrasal_verb": f"{verb} {particle}"})
        upsert_phrasal_verb = {"$set": phrasal_verb_info}
        rs = mongo.db.phrasal_verbs.update(
            search_query, upsert_phrasal_verb, upsert=True
        )
        return True

    except:
        traceback.print_exc()
        return False


def upsert_phrasal_verb_dictionary(phrasal_verb, data):
    try:
        search_query = gen_phrasal_verb_search_query(phrasal_verb)
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
        execute_command_ssh(os.getenv("CRAWLER"))

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
parser_dictionary.add_argument("datetime", type=str, required=True)
parser_dictionary.add_argument(
    "dictionaries", type=str, required=True, help="Source dictionaries", action="append"
)
parser_dictionary.add_argument(
    "definitions", type=str, help="Definitions", action="append"
)
parser_dictionary.add_argument("examples", type=str, help="Examples", action="append")

parser_random = reqparse.RequestParser()
parser_random.add_argument("count", type=int, location="args")


@api.route("/")
class PhrasalVerbs(Resource, CustomeResponse):
    @api.doc("list of phrasal_verbs")
    @api.expect(parser_search_verb, parser_header)
    @token_checker
    @return_500_for_sever_error
    def get(self, **kwargs):
        """List all phrasal verbs"""
        only_public = (
            False if kwargs["auth_user"] and kwargs["auth_user"].is_admin() else True
        )
        args = parser_search_verb.parse_args()
        result = get_verbs_from_phrasal_verbs(
            search_key=args["search_key"],
            full_search=args["full_search"],
            exact=args["exact"],
            only_public=only_public,
        )
        return self.send(response_type="SUCCESS", result=result)

    @api.doc("add a phrasal verb")
    @api.expect(parser_create, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        """Add an phrasal verb"""
        if not kwargs["auth_user"].is_admin():
            return self.send(response_type="FORBIDDEN")
        args = parser_create.parse_args()
        result = upsert_phrasal_verb(args)
        if result:
            start_crawler_job()
            return self.send(response_type="CREATED")
        else:
            return self.send(response_type="FAIL")

    @api.doc("delete a phrasal verb")
    @api.expect(parser_delete, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, **kwargs):
        """Delete an phrasal verb"""
        if not kwargs["auth_user"].is_admin():
            return self.send(response_type="FORBIDDEN")
        args = parser_delete.parse_args()
        result = delete_phrasal_verbs(args)
        status = "NO_CONTENT" if result else "FAIL"
        return self.send(status=status)


@api.route("/random")
class PhrasalVerbs(Resource, CustomeResponse):
    @api.expect(parser_random)
    @return_500_for_sever_error
    def get(self):
        """List random phrasal verbs"""
        args = parser_random.parse_args()
        return self.send(
            response_type="SUCCESS", result=get_random_public_verbs(args["count"])
        )


def get_phrasal_verb_with_dictionary(phrasal_verb):
    try:
        search_query = gen_phrasal_verb_search_query(phrasal_verb)
        return stringify_docs(mongo.db.phrasal_verbs.find(search_query))
    except:
        traceback.print_exc()
        return None


def get_verb_particle_from_phrasal_verb(phrasal_verb):
    result = None, None
    try:
        result = phrasal_verb.replace("-", " ").split(" ", 1)
        return result
    except:
        return result


@api.route("/<string:phrasal_verb>")
class PhrasalVerb(Resource, CustomeResponse):
    @api.doc("phrasal_verb")
    @api.expect(parser_header)
    @token_checker
    @return_500_for_sever_error
    def get(self, phrasal_verb, **kwargs):
        """Get a phrasal verb"""
        if kwargs["auth_user"] and kwargs["auth_user"].is_admin():
            result = get_phrasal_verb_with_dictionary(phrasal_verb)
        else:
            result = get_phrasal_verb(phrasal_verb)

        if result:
            return self.send(response_type="SUCCESS", result=result)
        else:
            return self.send(response_type="NOT_FOUND")

    @api.expect(parser_header, parser_dictionary)
    @token_checker
    @return_500_for_sever_error
    def put(self, phrasal_verb, **kwargs):
        if not kwargs["auth_user"].is_admin():
            return self.send(response_type="FORBIDDEN")
        args = parser_dictionary.parse_args()
        dictionary = {
            "definitions": args.definitions,
            "examples": args.examples,
            "sources": args.dictionaries,
            "uploaded_datetime": args.datetime,
        }
        if upsert_phrasal_verb_dictionary(phrasal_verb, dictionary):
            return self.send(response_type="SUCCESS")
        else:
            return self.send(response_type="FAIL")


@api.route("/likes")
class PhrasalVerbLikes(Resource, CustomeResponse):
    @api.doc("phrasal_verb")
    @api.expect(parser_get_phrasal_verb_like)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        args = parser_get_phrasal_verb_like.parse_args()
        result = {
            "count": get_phrasal_verbs_like(args["phrasal_verb_id"]),
            "active": get_user_like_active_status(
                kwargs["auth_user"], args["phrasal_verb_id"]
            ),
        }
        return self.send(response_type="SUCCESS", result=result)

    @api.expect(parser_like_create, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def post(self, **kwargs):
        args = parser_like_create.parse_args()
        result = update_user_like_phrasal_verb(kwargs["user_info"]["id"], args)
        if result:
            return self.send(response_type="SUCCESS")
        else:
            return self.send(response_type="FAIL")
