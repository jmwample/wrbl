from flask import Flask, abort, request, jsonify, g 
from functools import wraps
import config
import os
import psycopg2
import json
import yaml


#===============================[Init]=================================

app = Flask(__name__, instance_relative_config=True)

def main(app):

    if   app.config['ENV'] == 'development':
        app.config.from_object('config.DevelopmentConfig')
    elif app.config['ENV'] == 'production':
        app.config.from_object('config.ProductionConfig')
    elif app.config['ENV'] == 'testing':
        app.config.from_object('config.TestingConfig')
    else: 
        print("Unknown Environment please set FLASK_ENV to:\n\t1. development\n\t2. testing\n\t3. production")
        exit(1)

    init_db()

    app.run(host=app.config['HOST'], port = app.config['PORT'])


#===============================[Auth]=================================


def require_apikey(view_function):
    @wraps(view_function)
    # the new, post-decoration function. Note *args and **kwargs here.
    def decorated_function(*args, **kwargs):
        device_id = request.args.get('device_id')
        if not (device_id == None):
            if 'X-API-Key' in request.headers:
                api_key = request.headers['X-API-Key']
                if check_API_key(device_id, api_key):
                    return view_function(*args, **kwargs)
                else:
                    raise InvalidUsage('Unauthorized', status_code=401)
            else:
                raise InvalidUsage('Missing Auth Header', status_code=400)
        else:
            raise InvalidUsage('Missing Device ID', status_code=400)
    return decorated_function


def check_API_key(device_id, api_key):
    if api_key == get_api_key(device_id):
        return True
    else:
        return False


#==============================[Routes]================================

@app.route("/")
def hello():
    return "Hello World!"


@app.route("/api/upload", methods=["POST"])
@require_apikey
def upload():
    device_id = request.args.get('device_id')
    if request.data == None:
        return jsonify({'status':'success'})
    try:
        data_j = json.loads(request.data)
        commit_record(device_id, json.dumps(data_j))
    except json.JSONDecodeError as ex:
        InvalidUsage('JSON Format Error', status_code=400)
    return jsonify({'status':'success'})

@app.route("/api/test_key", methods=["POST"])
@require_apikey
def download():
    data = json.loads(request.data)
    print(data)
    return jsonify({'status':'success'})


#===========================[PSQL DB]==================================

def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = psycopg2.connect(app.config['PSQL_CONN_STR']) 
    return db


def init_db():
    print("Initializing database" )
    try: 
        db_admin = psycopg2.connect(app.config['PSQL_ADMIN_CONN_STR']) 
        with db_admin.cursor() as cursor:
            cursor.execute(open("api/init_schema.sql", "r").read())
            db_admin.commit()
    except Exception as ex:
        raise DatabaseError(str(ex), 500)
        exit(5)

def get_api_key(device_id):
    query_str = "SELECT device_api_key FROM devices WHERE device_id=%s" 
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str, (device_id,))
        # verify success
        if cursor.rowcount != 1:
            raise InvalidUsage('Unauthorized', status_code=401)
        api_key = cursor.fetchone()
        cursor.close()
        return api_key[0]
    except psycopg2.DataError as ex:
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except psycopg2.DatabaseError as ex:
        raise DatabaseError(str(ex), 500)

    

def commit_record(device_id, record):
    query_str = "INSERT INTO sensor_data (device_id, record) values (%s, %s)"
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str, (device_id, record))
        # verify success
        if cursor.rowcount != 1:
            raise DatabaseError('Rowcount error while inserting record',500, {'err_str':str(ex)})
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)


def create_experiment():
    pass

def update_experiment():
    pass

def results_experiment():
    pass

#=========================[Error Handling]================================

class InvalidUsage(Exception):
    status_code = 400

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        if app.config['DEBUG']:
            rv = dict(self.payload or ())
        else:
            rv = dict( () )
        rv['error'] = self.message
        rv['status'] = 'failure'
        return rv


class DatabaseError(Exception):
    status_code = 500  

    def __init__(self, message, status_code=None, payload=None):
        Exception.__init__(self)
        self.message = message
        if status_code is not None:
            self.status_code = status_code
        self.payload = payload

    def to_dict(self):
        if app.config['DEBUG']:
            rv = dict(self.payload or ())
        else:
            rv = dict( () )
        rv['error'] = self.message
        rv['status'] = 'failure'
        return rv

@app.errorhandler(InvalidUsage)
def handle_invalid_usage(error):
    response = jsonify(error.to_dict())
    response.status_code = error.status_code
    return response

@app.errorhandler(400)
@app.errorhandler(401)
@app.errorhandler(404)
def handle_api_error(ex):
    if request.path.startswith('/api/') and app.config['DEBUG']== True:
        response = jsonify({
            'status':'failure',
            'error':str(ex)})
        response.status_code = 404
        return response
    else:
        response = jsonify({'status':'failure'})
        response.status_code = 404
        return response

@app.errorhandler(500)
def handle_api_error(ex):
    if request.path.startswith('/api/') and app.config['DEBUG']== True:
        raise InvalidUsage(str(ex), 500) 
    else:
        raise InvalidUsage('Internal Server Error', 500) 


#=========================[Ready.. Go]================================
main(app)
