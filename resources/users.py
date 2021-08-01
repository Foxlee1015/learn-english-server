import traceback

from flask_restplus import Namespace, Resource, fields, reqparse

from core.db import insert_user, get_user, get_users, delete_users, backup_db, get_user_hashed_password_with_user_id
from core.resource import CustomResource, response, json_serializer_all_datetime_keys
from core.utils import execute_command_ssh, check_if_only_int_numbers_exist, verify_password


api = Namespace('users', description='Users related operations')

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

def get_user_if_user_verified(name, password):
    try:
        user_info = get_user_hashed_password_with_user_id(name)
        if user_info:
            if verify_password(password, user_info["salt"], user_info["password"]):
                return user_info
        return None
    except:
        traceback.print_exc()
        return None




parser_create = reqparse.RequestParser()
parser_create.add_argument('name', type=str, required=True, location='form', help='Unique user name')
parser_create.add_argument('email', type=str, location='form')
parser_create.add_argument('password', type=str, required=True, location='form', help='Password')
parser_create.add_argument('password_confirm', type=str, required=True, location='form', help='Confirm password')

parser_delete = reqparse.RequestParser()
parser_delete.add_argument('ids', type=str, required=True, action='split')



@api.route('/')
class Users(CustomResource):
    
    @api.doc('list_users')
    @api.response(203, 'User does not exist')
    def get(self):
        '''List all users
        
        NOTE: Only for admin users
        '''        
        users = _get_users()
        status = 200 if users else 203
        return self.send(status=status, result=users)


    @api.doc('create a new user')
    @api.expect(parser_create)
    @api.response(400, 'Password match error')
    @api.response(409, 'Duplicate user name')
    def post(self):
        '''Create an user'''
        args = parser_create.parse_args()
        name = args["name"]
        email = args["email"]
        password = args["password"]
        password_confirm = args["password_confirm"]
        
        if password_confirm != password:
            return self.send(status=400, message="Password and Confirm password have to be same")
        if get_user(name=name):
            return self.send(status=409, message="The given username alreay exists.")
        
        result = _create_user(name, email, password)
        status = 201 if result else 500
        return self.send(status=status)


    @api.doc('delete_users')
    @api.expect(parser_delete)
    @api.response(400, 'Check user ids')
    def delete(self):
        '''Delete all users
        
        NOTE: Only for admin users or user owner
        '''
        args = parser_delete.parse_args()
        ids = args['ids']
        if check_if_only_int_numbers_exist(ids):
            result = delete_users(args['ids'])
            return self.send(status=200)
        else:
            return self.send(status=400, message="Check user ids")

@api.route('/<int:id_>')
@api.param('id_', 'The user identifier')
@api.response(404, 'User not found')
class User(CustomResource):
    @api.doc('get_user')
    def get(self, id_):
        '''Fetch a user given its identifier'''
           
        user = get_user(id_=id_)
        if user is None:
            return self.send(status=404, result=None) 
        user = json_serializer_all_datetime_keys(user)
        return self.send(status=200, result=user)
        
    
    @api.doc('delete_user')
    def delete(self, id_):
        '''Delete an user'''
        result = delete_users([id_])
        return self.send(status=200)
