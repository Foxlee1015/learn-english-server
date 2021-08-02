import string
import random
import traceback
from flask_restplus import Namespace, reqparse

from core.db import redis_store
from .users import get_user_if_user_verified
from core.utils import token_required, random_string_digits
from core.resource import CustomResource

api = Namespace('sessions', description='Sessions related operations')


parser_create = reqparse.RequestParser()
parser_create.add_argument('username', type=str, required=True, help='Unique username')
parser_create.add_argument('password', type=str, required=True, help='Password')

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, required=True, location='headers')

@api.route('/')
@api.response(401, 'Session not found')
class Session(CustomResource):  
    @api.doc('create_session')
    @api.expect(parser_create)
    def post(self):
        '''Create a session after verifying user info '''
        try:
            args = parser_create.parse_args()
            user = get_user_if_user_verified(args["username"], args["password"])
            if user:
                session_id = random_string_digits(30)
                redis_store.set(name=session_id, value=user["id"], ex=60*60*24)
                return self.send(status=201, result=session_id)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc('delete_session')
    @api.expect(parser_header)
    def delete(self):
        '''User logout'''
        try:
            args = parser_header.parse_args()
            redis_store.delete(args["Authorization"])
            return self.send(status=200)
        except:
            traceback.print_exc()
            return self.send(status=500)

@api.route('/validate')
@api.response(401, 'Session is not valid')
class SessionVlidation(CustomResource):
    @api.doc('get_session')
    @api.expect(parser_header)
    @token_required
    def get(self, **kwargs):
        '''Check if session is valid'''
        try:
            status = 200 if kwargs["user_info"] is not None else 401
            return self.send(status=status)
        except:
            traceback.print_exc()
            return self.send(status=500)