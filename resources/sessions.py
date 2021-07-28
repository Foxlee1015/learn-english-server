from flask_restplus import Namespace, Resource, fields

api = Namespace('sessions', description='Sessions related operations')

sessions = [
    {'id': 1, 'name': 'a'},
    {'id': 2, 'name': 'b'},
    {'id': 3, 'name': 'c'},
]

@api.route('/<id>')
@api.param('id', 'The session identifier')
@api.response(404, 'Session not found')
class Session(Resource):
    @api.doc('get_sessions')
    def get(self, id):
        '''Fetch a session given its identifier'''
        for session in sessions:
            if session['id'] == id:
                return session
        api.abort(404)
    
    @api.doc('get_sessions')
    def post(self, id):
        '''Fetch a session given its identifier'''
        for session in sessions:
            if session['id'] == id:
                return session
        api.abort(404)

    @api.doc('get_sessions')
    def delete(self, id):
        '''Fetch a session given its identifier'''
        for session in sessions:
            if session['id'] == id:
                return session
        api.abort(404)