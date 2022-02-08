import time
from flask_restplus import Namespace, Resource
from threading import Thread

from app.core.variables import UPDATE_VERB_LIST_TIME
from app.core.mongo_db import get_all_unique_field_values

from app.core.response import (
    return_500_for_sever_error,
    CustomeResponse,
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
class particles(Resource, CustomeResponse):
    @api.doc("list_particles")
    @return_500_for_sever_error
    def get(self):
        return self.send(response_type="SUCCESS", result=unique_particles)
