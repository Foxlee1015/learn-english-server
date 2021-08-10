import json
from datetime import date, datetime

from flask import Response
from flask_restplus import Resource


class CustomResource(Resource):
    def __init__(self,api=None, *args, **kwargs):
        super().__init__(api, args, kwargs)

    def send(self, *args, **kwargs):
        headers = {}
        headers['Access-Control-Allow-Origin'] = '*'
        headers['Access-Control-Allow-Headers'] = '*'
        headers['Access-Control-Allow-Credentials'] = True

        response_body = {}
        response_body['result'] = kwargs.get('result')
        response_body['message'] = kwargs.get('message')
        
        json_encode = json.JSONEncoder().encode
        return Response(json_encode(response_body), status=kwargs["status"], 
                        headers=headers, mimetype="application/json")

    def is_admin(self, user_info):
        if user_info is None:
            return False
        if user_info["user_type"] == 0:
            return True
        return False


def response(**kwargs):
    params = ['status', 'message', 'result']
    for param in params:
        if kwargs.get(param) is None:
            kwargs[param] = None

    return kwargs


def json_serializer(obj, ignore_type_error=False):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()

    if ignore_type_error:
        return obj
    else:
        raise TypeError ("Type %s not serializable" % type(obj))
        

def json_serializer_all_datetime_keys(data):

    for key, value in data.items():
        data[key] = json_serializer(value, ignore_type_error=True)

    return data