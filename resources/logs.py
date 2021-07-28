from flask_restplus import Namespace, Resource, fields

api = Namespace('logs', description='Logs related operations')

logs = [
    {
        "id": 1,
        "name": 'water'
    },
    {
        "id": 2,
        "name": 'coke'
    }
]

@api.route('/')
class Logs(Resource):
    @api.doc('list_logs')
    def get(self):
        '''List all logs'''
        return logs

@api.route('/<id>')
@api.param('id', 'The log identifier')
@api.response(404, 'Log not found')
class Log(Resource):
    @api.doc('get_log')
    def get(self, id):
        '''Fetch a log given its identifier'''
        for log in logs:
            if log['id'] == id:
                return log
        api.abort(404)