import time
import traceback
from flask import Flask
from flask_cors import CORS

from resources import blueprint as api
from core.db import init_db, mongo_uri, mongo
from core.errors import DbConnectError

def init_settings():
    try:
        init_db()
    except DbConnectError as e:
        print(e)
    except:
        traceback.print_exc()

# thread
def background_task():
    while True:
        print("background_task")
        # backup_db()

def create_app():
    app = Flask(__name__)
    app.config['SECRET_KEY'] = "ssseetrr"
    app.config["MONGO_URI"] = mongo_uri
    mongo.init_app(app)
        
    CORS(app, resources={r"/api/*": {"origins": "*"}})

    app.register_blueprint(api, url_prefix='/api')
    # api.init_app(app) 
    # https://flask-restplus.readthedocs.io/en/stable/scaling.html
    # Calling Api.init_app() is not required here because registering the blueprint with the app takes care of setting up the routing for the application.
    init_settings()

    # background_task()

    return app
