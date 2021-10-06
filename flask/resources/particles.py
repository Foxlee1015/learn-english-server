import traceback
from flask_restplus import Namespace, reqparse


from core.db import get_particles, insert_particles, delete_particles

from core.resource import (
    CustomResource,
)
from core.utils import token_required
from resources.phrasal_verbs import get_all_unique_field_values

api = Namespace("particles", description="Particles related operations")

parser_create = reqparse.RequestParser()
parser_create.add_argument("name", type=str, required=True, help="Unique particle")

parser_header = reqparse.RequestParser()
parser_header.add_argument("Authorization", type=str, required=True, location="headers")


@api.route("/")
class Particles(CustomResource):
    @api.doc("list_particles")
    def get(self):
        try:
            return self.send(status=200, result=get_particles())
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
            if get_particles(name=name):
                return self.send(status=200)
            result = insert_particles(names=[name])
            if result:
                return self.send(status=201)
            else:
                return self.send(status=400)
        except:
            traceback.print_exc()
            return self.send(status=500)


@api.route("/<int:id_>")
@api.param("id", "The particle identifier")
class Particle(CustomResource):
    @api.doc("get_particle")
    def get(self, id_):
        particle = get_particles(id_=id_)
        if particle is None:
            return self.send(status=200, result=None)
        return self.send(status=200, result=particle)

    @api.doc("delete_particle")
    @api.expect(parser_header)
    @token_required
    def delete(self, id_, **kwargs):
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            result = delete_particles(ids=[id_])
            if result:
                return self.send(status=200)
            return self.send(status=400, message="Check particle id")

        except:
            traceback.print_exc()
            return self.send(status=500)

    @api.doc("update_particle")
    @api.expect(parser_create)
    def put(self, id_):
        # TODO
        # args = parser_create.parse_args()
        # name = args["name"]
        # user = update_particle(id_, name)
        return self.send(status=200)


@api.route("/async")
class AsyncParticles(CustomResource):
    @api.doc("async_particle")
    @api.expect(parser_header)
    @token_required
    def put(self, **kwargs):
        try:
            if not self.is_admin(kwargs["user_info"]):
                return self.send(status=403)
            particles = get_all_unique_field_values("particle")
            insert_particles(names=particles)
            return self.send(status=200)

        except:
            traceback.print_exc()
            return self.send(status=500)
