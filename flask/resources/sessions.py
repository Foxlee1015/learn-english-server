import traceback
from flask_restplus import Namespace, reqparse, Resource

from core.db import redis_store
from .users import get_user_if_verified
from core.utils import token_required, random_string_digits
from core.response import (
    CustomeResponse,
    return_401_for_no_auth,
    return_500_for_sever_error,
)
from core.variables import TOKEN_VALID_TIME

api = Namespace("sessions", description="Sessions related operations")


parser_create = reqparse.RequestParser()
parser_create.add_argument("username", type=str, required=True, help="Unique username")
parser_create.add_argument("password", type=str, required=True, help="Password")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")


def create_session(user_id):
    session_id = random_string_digits(30)
    redis_store.set(name=session_id, value=user_id, ex=TOKEN_VALID_TIME)
    return session_id


def set_user_info(user):
    return {"name": user["name"], "is_admin": 1 if user["user_type"] == 0 else 0}


@api.route("/")
class Session(Resource, CustomeResponse):
    @api.doc("create_session")
    @api.expect(parser_create)
    @return_500_for_sever_error
    def post(self):
        """Create a session after verifying user info"""
        args = parser_create.parse_args()
        user = get_user_if_verified(args["username"], args["password"])
        if user:
            result = {
                "user": user.username,
                "is_admin": 1 if user.is_admin() else 0,
                "session": create_session(user.id),
            }
            return self.send(response_type="CREATED", result=result)
        return self.send(
            response_type="FAIL", additional_message="Check your id and password."
        )

    @api.doc("delete_session")
    @api.expect(parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def delete(self):
        args = parser_header.parse_args()
        redis_store.delete(args["Authorization"])
        return self.send(response_type="NO_CONTENT")


@api.route("/validate")
@api.response(401, "Session is not valid")
class SessionVlidation(Resource, CustomeResponse):
    @api.doc("get_session")
    @api.expect(parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        """Check if session is valid"""
        result = {
            "user": kwargs["auth_user"].username,
            "is_admin": 1 if kwargs["auth_user"].is_admin() else 0,
        }
        return self.send(response_type="SUCCESS", result=result)
