from flask_restplus import Namespace, Resource

from app.core.mongo_db import (
    mongo,
    gen_not_include_query,
    gen_return_fields_query,
    stringify_docs,
)
from app.core.response import (
    return_500_for_sever_error,
    CustomeResponse,
)

api = Namespace("dictionaries", description="Dictionaries related operations")


def get_phrasal_verbs_to_search():
    query = gen_not_include_query(field="dictionaries")
    return_fields = gen_return_fields_query(
        includes=["phrasal_verb", "_id"],
    )
    return stringify_docs(mongo.db.phrasal_verbs.find(query, return_fields))


def get_idioms_to_search():
    query = gen_not_include_query(field="dictionaries")
    return_fields = gen_return_fields_query(
        includes=["expression", "_id"],
    )
    return stringify_docs(mongo.db.idioms.find(query, return_fields))


@api.route("/phrasal-verb")
class EmptyDictionary(Resource, CustomeResponse):
    @api.doc("add definitions and examples from dictionaries")
    @return_500_for_sever_error
    def get(self):
        return self.send(response_type="SUCCESS", result=get_phrasal_verbs_to_search())


@api.route("/idiom")
class EmptyDictionary(Resource, CustomeResponse):
    @api.doc("add definitions and examples from dictionaries")
    @return_500_for_sever_error
    def get(self):
        return self.send(response_type="SUCCESS", result=get_idioms_to_search())
