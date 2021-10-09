import time
import traceback
from flask import Flask
from flask_cors import CORS

from resources import blueprint as api
from core.db import init_db
from core.mongo_db import mongo_uri, mongo
from core.errors import DbConnectError
from resources.verbs import update_unique_verbs_job


def init_settings():
    try:
        init_db()
        set_mongodb_indexes()
    except DbConnectError as e:
        print(e)
    except:
        traceback.print_exc()


# thread
def background_task():
    update_unique_verbs_job()


def set_mongodb_indexes():
    print("set mongodb indexes")
    mongo.db.idioms.create_index([("$**", "text")])
    mongo.db.user_like_idiom.create_index([("userId", 1)])
    mongo.db.user_like_idiom.create_index([("idiomId", 1)])
    mongo.db.phrasal_verbs.create_index([("$**", "text")])
    mongo.db.user_like_phrasal_verb.create_index([("userId", 1)])
    mongo.db.user_like_phrasal_verb.create_index([("phrasalVerbId", 1)])


def create_app():
    app = Flask(__name__)
    app.config["SECRET_KEY"] = "ssseetrr"
    app.config["MONGO_URI"] = mongo_uri
    mongo.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api, url_prefix="/api")
    # api.init_app(app)
    # https://flask-restplus.readthedocs.io/en/stable/scaling.html
    # Calling Api.init_app() is not required here because registering the blueprint with the app takes care of setting up the routing for the application.
    init_settings()

    background_task()

    return app
