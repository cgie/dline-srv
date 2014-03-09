#!flask/bin/python

from datetime import datetime
from flask import Flask, jsonify, abort, make_response, request
from flask.ext.httpauth import HTTPBasicAuth
auth = HTTPBasicAuth()

@auth.get_password
def get_password(username):
    if username == 'user':
        return 'pass'
    return None

@auth.error_handler
def unauthorized():
    return make_response(jsonify( { 'error': 'Unauthorized access' } ), 401)

app = Flask(__name__)

deadlines = [
        {
            'id': 1,
            'title': 'Prepare food until noon',
            'deadline': datetime(2014, 3, 8, 12, 0)
        },
        {
            'id': 2,
            'title': 'finish RESTful API',
            'deadline': datetime(2014, 3, 8, 8, 0)
        }
]

@app.errorhandler(404)
@auth.login_required
def not_found(error):
        return make_response(jsonify( { 'error': 'Not found' } ), 404)

@app.route('/dline/api/v1.0/deadlines', methods = ['GET'])
@auth.login_required
def get_deadlines():
    return jsonify( { 'deadlines': deadlines} )

@app.route('/dline/api/v1.0/deadlines/<int:dl_id>', methods = ['GET'])
@auth.login_required
def get_deadline(dl_id):
    deadline = list(filter(lambda t: t['id'] == dl_id, deadlines))
    if len(deadline) == 0:
        abort(404)
    return jsonify( { 'deadline': deadline[0] } )

@app.route('/dline/api/v1.0/deadlines', methods = ['POST'])
@auth.login_required
def create_deadline():
    if not request.json or not 'title' in request.json:
        abort(400)
    deadline = {
        'id': deadlines[-1]['id'] + 1,
        'title': request.json['title'],
        'deadline': datetime.strptime(request.json['deadline'],'%Y-%m-%d %H:%M:%S')
    }
    deadlines.append(deadline)
    return jsonify( { 'deadline': deadline } ), 201

@app.route('/dline/api/v1.0/deadlines/<int:dl_id>', methods = ['PUT'])
@auth.login_required
def update_deadline(dl_id):
    deadline = list(filter(lambda t: t['id'] == dl_id, deadlines))
    if len(deadline) == 0:
        abort(404)
    if not request.json:
        abort(400)
    if 'title' in request.json and type(request.json['title']) is not str:
        abort(400)
    if 'deadline' in request.json and type(request.json['deadline']) is not str:
        abort(400)
    try: 
        deadlinedate = datetime.strptime(request.json['deadline'],'%Y-%m-%d %H:%M:%S')
    except ValueError:
        abort(400)

    deadline[0]['title'] = request.json.get('title', deadline[0]['title'])
    deadline[0]['deadline'] = request.json.get('deadline', deadline[0]['deadline'])
    return jsonify( { 'deadline': deadline[0] } )

@app.route('/dline/api/v1.0/deadlines/<int:dl_id>', methods = ['DELETE'])
@auth.login_required
def delete_deadline(dl_id):
    deadline = list(filter(lambda t: t['id'] == dl_id, deadlines))
    if len(deadline) == 0:
        abort(404)
    deadlines.remove(deadline[0])
    return jsonify( { 'result': True } )

if __name__ == '__main__':
    app.run(debug = True)
