import traceback
import redis
from flask import Flask
from flask_cors import CORS

from app.core.mongo_db import mongo
from config import config_by_name
from app.core.errors import DbConnectError
from app.resources.particles import update_unique_particles_job
from app.resources.users import delete_not_existing_users_likes
from app.core.database import db
from app.core.redis import redis_client

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
        from app.core.models import user, user_role
        try:
            result = db.create_all()
            db.session.commit()
        except:
            pass

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

    CORS(app, resources={r"/v1/*": {"origins": "*"}})
    db.init_app(app)
    set_db(app)
    redis_client.init_app(app)
    from app.resources import blueprint as api
    app.register_blueprint(api, url_prefix="/v1")
    init_settings()

    background_task()

    return app
