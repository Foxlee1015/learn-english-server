import os
from flask_pymongo import PyMongo
from dotenv import load_dotenv


# load dotenv in the base root
APP_ROOT = os.path.join(os.path.dirname(__file__), '..')   # refers to application_top
dotenv_path = os.path.join(APP_ROOT, '.env')
load_dotenv(dotenv_path)

mongo = PyMongo()
mongo_uri = os.getenv('MONGO_DB_URI')

def gen_query(field, search_key, exact=0, insensitive_case=True):
    # {"$text": {"$search": search_key}} 
    query = {}
    keyword = search_key # contain keyword
    if exact:
        keyword = f"^{search_key}$" # exact keyword
    
    query[field] = {"$regex": keyword} 
    if insensitive_case:
        query[field]["$options"]= "i"  # to match upper and lower cases
    
    return query


def gen_random_docs_query(count):
    return {"$sample": {"size":count}}

def gen_not_empty_array_query(field):
    return {f"{field}.0":{"$exists":"true"}}

def gen_match_and_query(filters):
    return {"$match":{"$and":filters}}

def stringify_docs(docs):
    items = []
    for data in docs:
        item = {}
        for key, value in data.items():
            if key == '_id': 
                value = str(value)
            if key == 'created_time':
                from core.resource import json_serializer
                value = json_serializer(value)
            item[key] = value
        items.append(item)
    return items

def gen_active_like_query(field_key, field_value, user_id=None):
    query = {
        field_key : field_value,
        "active": 1
    }
    if user_id is not None:
        query["userId"] = user_id

    return query