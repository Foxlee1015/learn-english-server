import traceback
import time
from flask_restplus import Namespace, reqparse
from threading import Thread

from core.variables import UPDATE_VERB_LIST_TIME
from resources.phrasal_verbs import get_all_unique_field_values

from core.resource import (
    CustomResource,
)

api = Namespace("verbs", description="Verbs related operations")


unique_verbs = []


def update_unique_verbs():
    while True:
        global unique_verbs
        unique_verbs = get_all_unique_field_values("verb")
        time.sleep(UPDATE_VERB_LIST_TIME)


def update_unique_verbs_job():
    thread = Thread(target=update_unique_verbs)
    thread.daemon = True
    thread.start()


@api.route("/")
class Verbs(CustomResource):
    @api.doc("list_verbs")
    def get(self):
        try:
            return self.send(status=200, result=unique_verbs)
        except:
            traceback.print_exc()
            return self.send(status=500)
