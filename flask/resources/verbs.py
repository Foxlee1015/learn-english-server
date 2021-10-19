import traceback
from flask_restplus import Namespace, reqparse

from core.mongo_db import (
    get_all_unique_field_values,
    gen_restrict_access_query,
)
from core.utils import token_required

from core.resource import (
    CustomResource,
)

api = Namespace("verbs", description="Verbs related operations")


unique_verbs = []

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Verbs(CustomResource):
    @api.doc("list_verbs")
    @api.expect(parser_header)
    @token_required
    def get(self, **kwargs):
        try:
            query = (
                {}
                if self.is_admin(kwargs["user_info"])
                else gen_restrict_access_query()
            )
            verbs = get_all_unique_field_values("verb", query=query)
            return self.send(status=200, result=verbs)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<string:verb>/particles")
class Verb(CustomResource):
    @api.expect(parser_header)
    @token_required
    def get(self, verb, **kwargs):
        try:
            query = {"verb": verb}
            if not self.is_admin(kwargs["user_info"]):
                query.update(gen_restrict_access_query())
            particles = get_all_unique_field_values("particle", query=query)
            return self.send(status=200, result=particles)
        except:
            traceback.print_exc()
            return self.send(status=500)
