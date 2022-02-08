from datetime import date, datetime

from flask_restplus import Resource

from flask import current_app, request
from app.core.response import CustomeResponse
from app.core.redis import redis_client

class CustomResource(Resource):
    def __init__(self, api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    def send(self, *args, **kwargs):
        return CustomeResponse.generate(
            kwargs.get("status"),
            result=kwargs.get("result"),
            message=kwargs.get("message"),
            response_type=kwargs.get("response_type"),
        )

    def is_admin(self, user_info):
        if user_info is None:
            return False
        if user_info["user_type"] == 0:
            return True
        return False


def token_checker(f):
    def wrapper(*args, **kwargs):
        user = None
        from app.core.models import User as UserModel

        if current_app.config["TESTING"]:
            return f(*args, **kwargs, auth_user=UserModel.query.get(1))
        if auth_header := request.headers.get("Authorization"):
            if user_id := redis_client.get(auth_header):
                user = UserModel.query.get(user_id)
        return f(*args, **kwargs, auth_user=user)

    wrapper.__doc__ = f.__doc__
    wrapper.__name__ = f.__name__
    return wrapper


def json_serializer(obj, ignore_type_error=False):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if ignore_type_error:
        return obj
    else:
        raise TypeError("Type %s not serializable" % type(obj))


def json_serializer_all_datetime_keys(data):
    if data:
        for key, value in data.items():
            data[key] = json_serializer(value, ignore_type_error=True)
    return data
