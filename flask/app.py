import traceback
from flask import Flask
from flask_cors import CORS

from resources import blueprint as api
from core.db import init_db
from core.mongo_db import mongo_uri, mongo
from core.config import config_by_name
from core.errors import DbConnectError
from core.utils import execute_command_ssh
from resources.particles import update_unique_particles_job
from core.database import db


def init_settings():
    try:
        init_db()
        execute_command_ssh("ls")
        set_mongodb_indexes()
    except DbConnectError as e:
        print(e)
    except:
        traceback.print_exc()


# thread
def background_task():
    update_unique_particles_job()


def set_db(app):
    with app.app_context():
        from core.models import user, user_role

        db.create_all()
        db.session.commit()


def set_mongodb_indexes():
    print("set mongodb indexes")
    mongo.db.idioms.create_index([("$**", "text")])
    mongo.db.user_like_idiom.create_index([("userId", 1)])
    mongo.db.user_like_idiom.create_index([("idiomId", 1)])
    mongo.db.phrasal_verbs.create_index([("$**", "text")])
    mongo.db.user_like_phrasal_verb.create_index([("userId", 1)])
    mongo.db.user_like_phrasal_verb.create_index([("phrasalVerbId", 1)])


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config_by_name[config_name])
    mongo.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    app.register_blueprint(api, url_prefix="/api")
    # api.init_app(app)
    # https://flask-restplus.readthedocs.io/en/stable/scaling.html
    # Calling Api.init_app() is not required here because registering the blueprint with the app takes care of setting up the routing for the application.
    init_settings()

    background_task()

    return app
