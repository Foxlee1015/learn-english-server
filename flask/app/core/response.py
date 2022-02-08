import traceback
import json

from flask import Response, current_app, request

from app.core.constants import response
from app.core.redis import redis_client


def return_401_for_no_auth(f):
    def wrapper(*args, **kwargs):
        user = None
        from app.core.models import User as UserModel

        if current_app.config["TESTING"]:
            return f(*args, **kwargs, auth_user=UserModel.query.get(1))
        if auth_header := request.headers.get("Authorization"):
            if user_id := redis_client.get(auth_header):
                user = UserModel.query.get(user_id)
        if user is not None:
            return f(*args, **kwargs, auth_user=user)
        else:
            response = CustomeResponse()
            return response.send(response_type="NO_AUTH")

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def return_500_for_sever_error(f):
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except:
            traceback.print_exc()
            response = CustomeResponse()
            return response.send(
                response_type="SEVER_ERROR",
            )

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


class CustomeResponse:
    headers = {
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Headers": "*",
        "Access-Control-Allow-Credentials": "True",
    }

    def send(
        self,
        result=None,
        response_type=None,
        lang="en",
        additional_message=None,
    ):

        status = response.status[response_type]
        message = response.message[lang][response_type]

        if additional_message is not None:
            message += f"({additional_message})"

        response_body = {"result": result, "message": message}

        json_encode = json.JSONEncoder().encode
        return Response(
            json_encode(response_body),
            status=status,
            headers=self.headers,
            mimetype="application/json",
        )


def gen_dupilcate_keys_message(keys, lang="en"):
    if lang == "en":
        return f"The given {(', ').join(keys)} already exist(s)."
    if lang == "kr":
        return f"{(', ').join(keys)} (들)은 이미 존재합니다."
