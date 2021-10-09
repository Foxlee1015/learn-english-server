import traceback
import time
from flask_restplus import Namespace, reqparse

from core.mongo_db import (
    mongo,
    gen_not_include_query,
    gen_return_fields_query,
    stringify_docs,
)
from core.resource import (
    CustomResource,
)

api = Namespace("dictionaries", description="Dictionaries related operations")


def get_phrasal_verbs_to_search():
    query = gen_not_include_query(field="dictionaires")
    return_fields = gen_return_fields_query(
        includes=["verb", "particle"], excludes=["_id"]
    )
    return stringify_docs(mongo.db.phrasal_verbs.find(query, return_fields))


@api.route("/empty")
class EmptyDictionary(CustomResource):
    @api.doc("add definitions and examples from dictionaries")
    def get(self, **kwargs):
        try:
            return self.send(status=200, result=get_phrasal_verbs_to_search())
        except:
            traceback.print_exc()
            return self.send(status=500)
