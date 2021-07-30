# -*- coding: utf-8 -*-
from datetime import datetime
import traceback
from bson import ObjectId
from flask import request
from flask_restplus import Namespace, Resource, fields, reqparse

from core.db import mongo
from core.resource import CustomResource, response, json_serializer, json_serializer_all_datetime_keys
from core.utils import check_if_only_int_numbers_exist, token_required, parse_given_str_datetime_or_current_datetime


api = Namespace('idioms', description='Idioms related operations')


def get_idioms():
    idioms = []
    for item in mongo.db.idioms.find():
        idiom = {}
        for key, value in item.items():
            if key == '_id': 
                value = str(value)
            if key == 'created_time': 
                value = json_serializer(value)
            
            idiom[key] = value
        idioms.append(idiom)
    
    return idioms

def add_idiom(args):
    try:
        args['created_time'] = datetime.now()
        print(args)
        mongo.db.idioms.insert_one(args)
        return True
    except:
        return False


def delete_idiom(args):
    query = {}
    if args["_id"] is not None:
        query["_id"] = ObjectId(args["_id"])
        
    if args["expression"] is not None:
        query["expression"] = args["expression"]

    items = mongo.db.idioms.find(query)
    if items:
        for item in items:
            print(item)
            for key, value in item.items():
                print(key, value)
        
    try:
        print(query)
        mongo.db.idioms.delete_many(query)
        return True
    except:
        traceback.print_exc()
        return False


parser_create = reqparse.RequestParser()
parser_create.add_argument('expression', type=str, required=True, help='Expression')
parser_create.add_argument('definitions', type=str, help='Definitions', action='append')
parser_create.add_argument('sentences', type=str, help='Sentences', action='append')
parser_create.add_argument('level', type=int, help='Learning level')



parser_delete = reqparse.RequestParser()
parser_delete.add_argument('_id', type=str, help='_id', location="args")
parser_delete.add_argument('expression', type=str, help='Expression', location="args")


@api.route('/')
class Idioms(CustomResource):
    @api.doc('list_idioms')
    @api.response(203, 'Idiom does not exist')
    def get(self):
        '''List all idioms'''     
        result = get_idioms()
        status = 200 if result else 203
        return self.send(status=status, result=result)

    
    @api.doc('add an idiom')
    @api.expect(parser_create)
    @api.response(409, 'Duplicate idiom')
    def post(self):
        '''Add an idiom'''
        
        # request.get_json(force=True)
        args = parser_create.parse_args()
        result = add_idiom(args)
        status = 201 if result else 400
        
        return self.send(status=status)

    @api.doc('delete an idiom')
    @api.expect(parser_delete)
    def delete(self):
        '''Delete an idiom'''
        
        args = parser_delete.parse_args()
        result = delete_idiom(args)
        status = 200 if result else 400
        
        return self.send(status=status)