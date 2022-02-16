from flask import Blueprint
from flask_restplus import Api

from .logs import api as logs
from .sessions import api as sessions
from .idioms import api as idioms
from .phrasal_verbs import api as phrasal_verbs
from .users import api as users
from .verbs import api as verbs
from .particles import api as particles
from .dictionaries import api as dictionaries

blueprint = Blueprint("v1", __name__)
api = Api(blueprint, title="Learn English API", version="1.0", description="")

api.add_namespace(phrasal_verbs)
api.add_namespace(idioms)
api.add_namespace(logs)
api.add_namespace(sessions)
api.add_namespace(users)
api.add_namespace(verbs)
api.add_namespace(particles)
api.add_namespace(dictionaries)
