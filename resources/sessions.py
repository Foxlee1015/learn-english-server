import string
import random
from flask_restplus import Namespace, Resource, reqparse

from core.db import get_session, redis_store
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
@api.response(404, 'Session not found')
class Session(CustomResource):
    
    @api.doc('get_sessions')
    @api.expect(parser_header)
    @token_required
    def get(self, **kwargs):
        status = 200 if kwargs["user_id"] is not None else 400
        print(kwargs["user_id"])
        return self.send(status=status)
    
    @api.doc('create_sessions')
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

    @api.doc('delete_sessions')
    @api.expect(parser_header)
    def delete(self):
        args = parser_header.parse_args()
        '''User logout'''
        print(args)
        redis_store.delete(args["Authorization"])
        return self.send(status=200)