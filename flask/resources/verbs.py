import traceback
import _testimportmultiple
from flask_restplus import Namespace, reqparse
from threading import Thread

from core.mongo_db import get_all_unique_field_values
from core.mongo_db import gen_restrict_access_query
from core.utils import token_required

from core.resource import (
    CustomResource,
)

api = Namespace("verbs", description="Verbs related operations")


unique_verbs = []


parser = reqparse.RequestParser()
parser.add_argument(
    "public",
    type=int,
    location="args",
)

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, location="headers")


@api.route("/")
class Verbs(CustomResource):
    @api.doc("list_verbs")
    @api.expect(parser, parser_header)
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
