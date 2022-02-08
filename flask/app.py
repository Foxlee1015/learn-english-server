import traceback
from flask import Flask
from flask_cors import CORS

from resources import blueprint as api
from core.mongo_db import mongo
from core.config import config_by_name
from core.errors import DbConnectError
from resources.particles import update_unique_particles_job
from resources.users import delete_not_existing_users_likes
from core.database import db

config = None

def init_settings():
    try:
        delete_not_existing_users_likes()
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
    app_config = config_by_name[config_name]
    app.config.from_object(app_config)
    global config
    config = app_config
    mongo.init_app(app)

    CORS(app, resources={r"/api/*": {"origins": "*"}})
    db.init_app(app)

    app.register_blueprint(api, url_prefix="/api")
    init_settings()

    background_task()

    return app
