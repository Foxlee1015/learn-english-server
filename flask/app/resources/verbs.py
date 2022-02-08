from flask_restplus import Namespace, reqparse, Resource

from app.core.mongo_db import (
    get_all_unique_field_values,
    gen_restrict_access_query,
)
from app.core.response import (
    return_500_for_sever_error,
    return_401_for_no_auth,
    CustomeResponse,
)

api = Namespace("verbs", description="Verbs related operations")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Verbs(Resource, CustomeResponse):
    @api.doc("list_verbs")
    @api.expect(parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, **kwargs):
        query = {} if kwargs["auth_user"].is_admin() else gen_restrict_access_query()
        verbs = get_all_unique_field_values("verb", query=query)
        return self.send(response_type="SUCCESS", result=verbs)


@api.route("/<string:verb>/particles")
class Verb(Resource, CustomeResponse):
    @api.expect(parser_header)
    @return_401_for_no_auth
    @return_500_for_sever_error
    def get(self, verb, **kwargs):
        query = {"verb": verb}
        if not kwargs["auth_user"].is_admin():
            query.update(gen_restrict_access_query())
        particles = get_all_unique_field_values("particle", query=query)
        return self.send(response_type="SUCCESS", result=particles)
