import traceback
from bson import ObjectId

from flask_restplus import Namespace, Resource, fields, reqparse

from core.db import (
    insert_user,
    get_user,
    get_users,
    delete_users,
    backup_db,
    get_user_hashed_password_with_user_id,
)
from core.resource import (
    CustomResource,
    json_serializer,
    json_serializer_all_datetime_keys,
)
from core.utils import token_required, verify_password
from core.mongo_db import mongo, gen_user_like_query, stringify_docs, gen_in_query


api = Namespace("users", description="Users related operations")


def _get_users():
    try:
        users = get_users()
        for user in users:
            user = json_serializer_all_datetime_keys(user)
        return users
    except:
        traceback.print_exc()
        return None


def _create_user(name, email, password, user_type=2):
    try:
        result = insert_user(name, email, password, user_type)
        return result
    except:
        traceback.print_exc()
        return None


def get_user_if_verified(name, password):
    try:
        user_info = get_user_hashed_password_with_user_id(name)
        if user_info:
            if verify_password(password, user_info["salt"], user_info["password"]):
                return get_user(id_=user_info["id"])
        return None
    except:
        traceback.print_exc()
        return None


def get_user_idioms_count(user_id):
    try:
        query = gen_user_like_query(user_id)
        return mongo.db.user_like_idiom.find(query).count()
    except:
        traceback.print_exc()
        return None


def get_user_idioms(user_id):
    try:
        likes_query = gen_user_like_query(user_id)
        idioms_ids = []
        for item in mongo.db.user_like_idiom.find(likes_query):
            for key, value in item.items():
                if key == "idiomId":
                    idioms_ids.append(ObjectId(value))
        idioms_query = gen_in_query(field="_id", values=idioms_ids)
        return stringify_docs(mongo.db.idioms.find(idioms_query))

    except:
        traceback.print_exc()
        return None


def get_user_phrasal_verbs_count(user_id):
    try:
        query = gen_user_like_query(user_id)
        return mongo.db.user_like_phrasal_verb.find(query).count()
    except:
        traceback.print_exc()
        return None


def get_user_phrasal_verbs(user_id):
    try:
        likes_query = gen_user_like_query(user_id)
        phrasal_verbs_ids = []
        for item in mongo.db.user_like_phrasal_verb.find(likes_query):
            for key, value in item.items():
                if key == "phrasalVerbId":
                    phrasal_verbs_ids.append(ObjectId(value))
        phrasal_verbs_query = gen_in_query(field="_id", values=phrasal_verbs_ids)
        return stringify_docs(mongo.db.phrasal_verbs.find(phrasal_verbs_query))

    except:
        traceback.print_exc()
        return None


parser_create = reqparse.RequestParser()
parser_create.add_argument(
    "name", type=str, required=True, location="form", help="Unique user name"
)
parser_create.add_argument("email", type=str, location="form")
parser_create.add_argument(
    "password", type=str, required=True, location="form", help="Password"
)
parser_create.add_argument(
    "password_confirm",
    type=str,
    required=True,
    location="form",
    help="Confirm password",
)

parser_delete = reqparse.RequestParser()
parser_delete.add_argument("ids", type=str, required=True, action="split")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")

parser_likes = reqparse.RequestParser()
parser_likes.add_argument("count", type=int, location="args", help="When constant true")


@api.route("/")
class Users(CustomResource):
    @api.doc("list_users")
    @api.expect(parser_header)
    @token_required
    def get(self, **kwargs):
        """List all users

        NOTE: Only for admin users
        """
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            return self.send(status=200, result=_get_users())
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("create a new user")
    @api.expect(parser_create)
    def post(self):
        """Create an user"""
        try:
            args = parser_create.parse_args()
            name = args["name"]
            email = args["email"]
            password = args["password"]
            password_confirm = args["password_confirm"]

            if password_confirm != password:
                return self.send(
                    status=400, message="Password and Confirm password have to be same"
                )
            if get_user(name=name):
                return self.send(
                    status=400, message="The given username alreay exists."
                )

            result = _create_user(name, email, password)
            if result:
                return self.send(status=201)
            else:
                return self.send(status=500)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("delete_users")
    @api.expect(parser_delete, parser_header)
    @token_required
    def delete(self, **kwargs):
        """Delete all users

        NOTE: Only for admin users or user owner
        """
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)

            args = parser_delete.parse_args()
            result = delete_users(args["ids"])
            if result:
                return self.send(status=200)
            return self.send(status=400, message="Check user ids")

        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id_>")
@api.param("id_", "The user identifier")
class User(CustomResource):
    @api.doc("get_user")
    @api.expect(parser_header)
    @token_required
    def get(self, id_, **kwargs):
        """Fetch a user given its identifier"""
        if kwargs["user_info"] is None:
            return self.send(status=401)
        if self.is_admin(kwargs["user_info"]) or id_ == kwargs["user_info"]["id"]:
            user = get_user(id_=id_)
            if user:
                user = json_serializer_all_datetime_keys(user)
                return self.send(status=200, result=user)
            else:
                return self.send(status=404)
        else:
            return self.send(status=401)


@api.route("/idioms")
class UserLikesIdioms(CustomResource):
    @api.doc("get_user_idioms_likes")
    @api.expect(parser_header, parser_likes)
    @token_required
    def get(self, **kwargs):
        try:
            if kwargs["user_info"] is None:
                return self.send(status=401)
            user_id = kwargs["user_info"]["id"]

            args = parser_likes.parse_args()
            if args["count"]:
                result = get_user_idioms_count(user_id)
            else:
                result = get_user_idioms(user_id)

            if result is None:
                return self.send(status=500)

            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/phrasal-verbs")
class UserLikesPhrasalVerbs(CustomResource):
    @api.doc("get_user_phrasal_verbs_likes")
    @api.expect(parser_header, parser_likes)
    @token_required
    def get(self, **kwargs):
        try:
            if kwargs["user_info"] is None:
                return self.send(status=401)
            user_id = kwargs["user_info"]["id"]

            args = parser_likes.parse_args()
            if args["count"]:
                result = get_user_phrasal_verbs_count(user_id)
            else:
                result = get_user_phrasal_verbs(user_id)

            if result is None:
                return self.send(status=500)

            return self.send(status=200, result=result)
        except:
            traceback.print_exc()
            return self.send(status=500)
