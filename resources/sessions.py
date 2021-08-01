import string
import random
from flask_restplus import Namespace, Resource, reqparse

from core.db import redis_store
from .users import get_user_if_user_verified
from core.utils import token_required
from core.resource import CustomResource, response, json_serializer

api = Namespace('sessions', description='Sessions related operations')


parser_create = reqparse.RequestParser()
parser_create.add_argument('username', type=str, required=True, help='Unique username')
parser_create.add_argument('password', type=str, required=True, help='Password')

parser_header = reqparse.RequestParser()
parser_header.add_argument('Authorization', type=str, location='headers')

@api.route('/')
@api.response(401, 'Session not found')
class Session(CustomResource):  
    @api.doc('create_session')
    @api.expect(parser_create)
    def post(self):
        '''Create a session after verifying user info '''
        session_id = None
        args = parser_create.parse_args()
        user = get_user_if_user_verified(args["username"], args["password"])
        if user:
            session_id = ''.join(random.choice(string.ascii_letters + string.digits) for _ in range(30))
            redis_store.set(name=session_id, value=user["id"], ex=1000)
        
        status = 201 if session_id is not None else 400
        return self.send(status=status, result=session_id)

    @api.doc('delete_session')
    @api.expect(parser_header)
    def delete(self):
        '''User logout'''
        args = parser_header.parse_args()
        redis_store.delete(args["Authorization"])
        return self.send(status=200)


@api.route('/validate')
@api.response(401, 'Session is not valid')
class SessionVlidation(CustomResource):
    
    @api.doc('get_session')
    @api.expect(parser_header)
    @token_required
    def get(self, **kwargs):
        '''Check if session is valid'''
        status = 200 if kwargs["user_info"] is not None else 401
        return self.send(status=status)