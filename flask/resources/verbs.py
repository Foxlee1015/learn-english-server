import traceback
from flask_restplus import Namespace, reqparse


from core.db import get_verbs, insert_verbs, delete_verbs

from core.resource import (
    CustomResource,
)
from core.utils import token_required
from resources.phrasal_verbs import get_all_unique_field_values, sync_phrasal_verbs

api = Namespace("verbs", description="Verbs related operations")

parser_create = reqparse.RequestParser()
parser_create.add_argument("name", type=str, required=True, help="Unique verb")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")


@api.route("/")
class Verbs(CustomResource):
    @api.doc("list_verbs")
    def get(self):
        try:
            return self.send(status=200, result=get_verbs())
        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.expect(parser_create, parser_header)
    @token_required
    def post(self, **kwargs):
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)

            args = parser_create.parse_args()
            name = args["name"]
            if get_verbs(name=name):
                return self.send(status=200)
            result = insert_verbs(names=[name])
            if result:
                # sync_phrasal_verbs()
                return self.send(status=201)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id_>")
@api.param("id", "The verb identifier")
class verb(CustomResource):
    @api.doc("get_verb")
    def get(self, id_):
        verb = get_verbs(id_=id_)
        if verb is None:
            return self.send(status=200, result=None)
        return self.send(status=200, result=verb)

    @api.doc("delete_verb")
    @api.expect(parser_header)
    @token_required
    def delete(self, id_, **kwargs):
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            result = delete_verbs(ids=[id_])
            if result:
                return self.send(status=200)
            return self.send(status=400, message="Check verb id")

        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/async")
class AsyncVerbs(CustomResource):
    @api.doc("async_verb")
    @api.expect(parser_header)
    @token_required
    def put(self, **kwargs):
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            verbs = get_all_unique_field_values("verb")
            insert_verbs(names=verbs)
            return self.send(status=200)

        except:
            traceback.print_exc()
            return self.send(status=500)
