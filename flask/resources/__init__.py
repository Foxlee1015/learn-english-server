from flask import Blueprint
from flask_restplus import Api
import jwt

from .logs import api as logs
from .sessions import api as sessions
from .idioms import api as idioms
from .phrasal_verbs import api as phrasal_verbs
from .users import api as users
from .particles import api as particles

blueprint = Blueprint("api", __name__)
api = Api(blueprint, title="Learn English API", version="1.0", description="")

api.add_namespace(phrasal_verbs)
api.add_namespace(idioms)
api.add_namespace(logs)
api.add_namespace(sessions)
api.add_namespace(users)
api.add_namespace(particles)
