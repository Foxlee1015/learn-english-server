import traceback
from bson import ObjectId

from flask_restplus import Namespace, reqparse, Resource
from app.core.response import (
    return_500_for_sever_error,
    return_401_for_no_auth,
    gen_dupilcate_keys_message,
    CustomeResponse,
)

from app.core.models import User as UserModel, UserRole as UserRoleModel
from app.core.database import db, get_db_session
from app.core.mongo_db import mongo, gen_user_like_query, stringify_docs, gen_in_query


api = Namespace("users", description="Users related operations")


def get_users() -> list:
    users = UserModel.query.all()
    return [user.serialize for user in users]


def get_user_if_verified(username, password):
    user = UserModel.query.filter_by(username=username).first()
    if user:
        if user.check_password(password):
            return user
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


def get_user_by_username(username) -> dict:
    user = UserModel.query.filter_by(username=username).first()
    return user.serialize if user else None


def get_user_by_email(email) -> dict:
    user = UserModel.query.filter_by(email=email).first()
    return user.serialize if user else None


def check_user_info_duplicates(args) -> list:
    result = []
    if args.get("username") is not None:
        if get_user_by_username(args.get("username")):
            result.append("username")

    if args.get("email") is not None:
        if get_user_by_email(args.get("email")):
            result.append("email")
    return result


def get_user_by_id(id_) -> dict:
    user = UserModel.query.get(id_)
    return user.serialize if user else None


def create_user(args) -> dict:
    general_user_role = UserRoleModel.query.filter_by(name="general").first()
    user = UserModel(
        args["name"], args.get("email"), args["password"], general_user_role.id
    )
    user.create()
    return user


def delete_user(id_) -> None:
    UserModel.query.filter_by(id=id_).delete()
    db.session.commit()


def update_user(user, arg) -> None:
    if arg["password"] is not None:
        user.password = UserModel.generate_hashed_password(arg["password"])
    if arg["email"] is not None:
        user.email = arg["email"]
    db.session.commit()


def delete_not_existing_users_likes():
    db_scoped_session = get_db_session()
    db_session = db_scoped_session()

    idiom_like_users = mongo.db.user_like_idiom.distinct("userId", {})
    for user_id in idiom_like_users:
        try:
            db_session.query(UserModel).filter_by(id=user_id).one()
        except:
            mongo.db.user_like_idiom.delete_many({"userId": user_id})
    
    phrasal_verb_like_users = mongo.db.user_like_phrasal_verb.distinct("userId", {}) 
    for user_id in phrasal_verb_like_users:
        try:
            db_session.query(UserModel).filter_by(id=user_id).one()
        except:
            mongo.db.user_like_phrasal_verb.delete_many({"userId": user_id})


def delete_user_likes(user_id):
    mongo.db.user_like_idiom.delete_many({"userId": user_id})
    mongo.db.user_like_phrasal_verb.delete_many({"userId": user_id})


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
class Users(Resource, CustomeResponse):
    @api.doc("list_users")
    @api.expect(parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        """List all users

        NOTE: Only for admin users
        """
        if kwargs["auth_user"].is_admin():
            return self.send(response_type="SUCCESS", result=get_users())

        return self.send(response_type="FORBIDDEN")

    @api.doc("create a new user")
    @api.expect(parser_create)
    @return_500_for_sever_error
    def post(self):
        """Create an user"""
        args = parser_create.parse_args()
        if duplicate_keys := check_user_info_duplicates(args):
            return self.send(
                response_type="FAIL",
                additional_message=gen_dupilcate_keys_message(duplicate_keys),
            )
        result = create_user(args)
        return self.send(response_type="CREATED", result=result.id)


@api.route("/<int:id_>")
@api.param("id_", "The user identifier")
class User(Resource, CustomeResponse):
    @api.doc("get_user")
    @api.expect(parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, id_, **kwargs):
        """Fetch a user given its identifier"""
        if user := get_user_by_id(id_):
            if kwargs["auth_user"].is_admin() or kwargs["auth_user"].id == id_:
                return self.send(response_type="SUCCESS", result=user)
        return self.send(response_type="NOT_FOUND")

    @api.doc("delete_users")
    @api.expect(parser_delete, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self, id_, **kwargs):
        """Delete a user

        NOTE: Only for admin
        """
        if get_user_by_id(id_):
            if kwargs["auth_user"].is_admin():
                delete_user(id_)
                delete_user_likes(id_)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")

    @api.expect(parser_create, parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def put(self, id_, **kwargs):
        if UserModel.get_by_id(id_):
            if kwargs["auth_user"].is_admin():
                args = parser_create.parse_args()
                update_user(UserModel.query.get(id_), args)
                return self.send(response_type="NO_CONTENT")
            return self.send(response_type="FORBIDDEN")
        return self.send(response_type="NOT_FOUND")


@api.route("/idioms")
class UserLikesIdioms(Resource, CustomeResponse):
    @api.doc("get_user_idioms_likes")
    @api.expect(parser_header, parser_likes)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        user_id = kwargs["auth_user"].id
        args = parser_likes.parse_args()
        result = (
            get_user_idioms_count(user_id)
            if args["count"]
            else get_user_idioms(user_id)
        )
        return self.send(response_type="SUCCESS", result=result)


@api.route("/phrasal-verbs")
class UserLikesPhrasalVerbs(Resource, CustomeResponse):
    @api.doc("get_user_phrasal_verbs_likes")
    @api.expect(parser_header, parser_likes)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        user_id = kwargs["auth_user"].id
        args = parser_likes.parse_args()
        result = (
            get_user_phrasal_verbs_count(user_id)
            if args["count"]
            else get_user_phrasal_verbs(user_id)
        )
        return self.send(response_type="SUCCESS", result=result)
