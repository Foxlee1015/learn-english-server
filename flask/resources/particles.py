import traceback
import time
from flask_restplus import Namespace, reqparse
from threading import Thread

from core.variables import UPDATE_VERB_LIST_TIME
from core.mongo_db import get_all_unique_field_values

from core.resource import (
    CustomResource,
)

api = Namespace("particles", description="particles related operations")


unique_particles = []


def update_unique_particles():
    while True:
        global unique_particles
        unique_particles = get_all_unique_field_values("particle")
        time.sleep(UPDATE_VERB_LIST_TIME)


def update_unique_particles_job():
    thread = Thread(target=update_unique_particles)
    thread.daemon = True
    thread.start()


@api.route("/")
class particles(CustomResource):
    @api.doc("list_particles")
    def get(self):
        try:
            return self.send(status=200, result=unique_particles)
        except:
            traceback.print_exc()
            return self.send(status=500)
