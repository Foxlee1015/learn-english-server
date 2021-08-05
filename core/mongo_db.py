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