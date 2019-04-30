from flask import Flask, abort, request, jsonify, g, render_template, send_from_directory, redirect, Response
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired
from functools import wraps
import requests 
import datetime
import config
import os
import psycopg2
import json
import yaml


#===============================[Init]=================================

app = Flask(__name__, instance_relative_config=True, static_url_path='/static')

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


def require_key(view_function):
    """
    Checks for device_id and api_key in form AND in Headers.
    """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # Find Device ID either in args or in form 
        device_id = request.args.get('device_id')
        if device_id == None:
            device_id = request.form['device_id']

        if not (device_id == None):
            # Check for key in headers
            if 'X-API-Key' in request.headers:
                api_key = request.headers['X-API-Key']
                if check_API_key(device_id, api_key):
                    return view_function(*args, **kwargs)
                else:
                    raise InvalidUsage('Unauthorized', status_code=401)

            # Check for key in form
            elif not (request.form['api_key'] == None):
                api_key = request.form['api_key']
                if check_API_key(device_id, api_key):
                    return view_function(*args, **kwargs)
                else:
                    raise InvalidUsage('Unauthorized', status_code=401)

            # Api_key not provided
            else:
                raise InvalidUsage('Missing Auth Header', status_code=400)
        else:
            raise InvalidUsage('Missing Device ID', status_code=400)
    return decorated_function


def require_formkey(view_function):
    """
    Checks for device_id and api_key in form AND in Headers.
    """
    @wraps(view_function)
    def decorated_function(*args, **kwargs):
        # Find Device ID either in args or in form 
        device_id = request.form['device_id']

        if not (device_id == None):
            # Check for key in form
            if not (request.form['api_key'] == None):
                api_key = request.form['api_key']
                if check_API_key(device_id, api_key):
                    return view_function(*args, **kwargs)
                else:
                    raise InvalidUsage('Unauthorized', status_code=401)
            # Api_key not provided
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
def landing():
    ex_key = "XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX"
    ex_id = "XXXXXXXX-XXXX-XXXX-XXXX-XXXXXXXXXXXX"
    return render_template("index.html", 
        example_api_key=ex_key, 
        example_device_id=ex_id)


@app.route('/img/<path:path>')
def send_js(path):
    return send_from_directory('static/images', path)

@app.route("/device", methods=["POST"])
@require_formkey
def device_landing():
    device_id = request.form['device_id']
    api_key = request.form['api_key']

    # Collect data for device template
    data = get_device_info(device_id)
    
    return render_template("device.html", device_id=device_id, api_key=api_key, data=data)


@app.route("/api/experiment/create", methods=["POST"])
@require_formkey
def create_experiment():
    device_id = request.form['device_id']
    api_key = request.form['api_key']
    labels = [x.strip() for x in request.form['labels'].split(',')]

    # Create Experiment
    create_experiment_basic(device_id, labels)

    # Collect data for device template
    data = get_device_info(device_id)

    return render_template("device.html", device_id=device_id, api_key=api_key, data=data)


@app.route("/api/upload", methods=["POST"])
@require_apikey
def upload():
    device_id = request.args.get('device_id')
    if request.data == None:
        return jsonify({'status':'success'})
    try:
        data_j = json.loads(request.data)
        for sample in data_j:
            commit_record(device_id, json.dumps(sample))
    except json.JSONDecodeError as ex:
        InvalidUsage('JSON Format Error', status_code=400)
    return jsonify({'status':'success'})


@app.route("/api/experiment/update-test/<ex_id>", methods=["POST", "GET"])
def ex_update_to_test(ex_id):
    device_id = request.args.get('device_id')
    api_key = request.args.get('device_api_key')
	
    print(device_id, api_key, ex_id)
    if check_API_key(device_id, api_key):
        ex_Test(device_id, ex_id)

    # Collect data for device template
    data = get_device_info(device_id)

    return render_template("device.html", device_id=device_id, api_key=api_key, data=data)



@app.route("/api/experiment/update-complete/<ex_id>", methods=["POST", "GET"])
def ex_update_to_complete(ex_id):
    device_id = request.args.get('device_id')
    api_key = request.args.get('device_api_key')

    if check_API_key(device_id, api_key):
        ex_Complete(device_id, ex_id)

    # Collect data for device template
    data = get_device_info(device_id)

    return render_template("device.html", device_id=device_id, api_key=api_key, data=data)



@app.route("/api/experiment/cancel/<ex_id>", methods=["POST", "GET"])
def ex_cancel(ex_id):
    device_id = request.args.get('device_id')
    api_key = request.args.get('device_api_key')

    if check_API_key(device_id, api_key):
        ex_Cancel(device_id, ex_id)

    # Collect data for device template
    data = get_device_info(device_id)

    return render_template("device.html", device_id=device_id, api_key=api_key, data=data)


@app.route("/api/experiment/evaluate/<ex_id>", methods=["POST", "GET"])
def ex_evaluate(ex_id):
    device_id = request.args.get('device_id')
    api_key = request.args.get('device_api_key')

    if check_API_key(device_id, api_key):
        ex_Evaluate(device_id, ex_id)

    # Collect data for device template
    data = get_device_info(device_id)

    return render_template("device.html", device_id=device_id, api_key=api_key, data=data)


@app.route("/api/test_key", methods=["POST"])
@require_apikey
def download():
    data = json.loads(request.data)
    # print(data)
    return jsonify({'status':'success'})



@app.route('/grafana/', defaults={'path': ''})
@app.route('/grafana/<path:path>')
def _proxy(*args, **kwargs):

	# API KEY FOR GRAPHANA
	# curl -H "Authorization: Bearer eyJrIjoiYUk2Z0ZNUVk0Z3J4Y01FN2k5d3RwaTZMcjZWeG5lem0iLCJuIjoidmlld19zdGF0cyIsImlkIjoxfQ==" http://localhost:8080/api/dashboards/home
	# headers = {key: value for (key, value) in request.headers if key != 'Host'}
	headers = {}
	headers['Authorization'] =  'Bearer eyJrIjoiYUk2Z0ZNUVk0Z3J4Y01FN2k5d3RwaTZMcjZWeG5lem0iLCJuIjoidmlld19zdGF0cyIsImlkIjoxfQ=='

	resp = requests.request(
		method=request.method,
		url=request.url.replace(request.host_url+'grafana', f'http://localhost:3000'),
		headers=headers,
		data=request.get_data(),
		cookies=request.cookies,
		allow_redirects=False)



	excluded_headers = ['content-encoding', 'content-length', 'transfer-encoding', 'connection']
	headers = [(name, value) for (name, value) in resp.raw.headers.items()
			   if name.lower() not in excluded_headers]

	response = Response(resp.content, resp.status_code, headers)
	return response

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


def get_experiments_by_device(cursor, device_id):
    query_str = """
    SELECT experiment_id, device_id, 
    extract(epoch from ctrl_start) as ctrl_start, extract(epoch from ctrl_end) as ctrl_end, ctrl_dur,
    extract(epoch from test_start) as test_start, extract(epoch from test_end) as test_end, test_dur,
    fields, labels, graph_path, status
    FROM experiments where device_id = %s order by experiment_id;
    """
    cursor.execute(query_str, (device_id,))
    if cursor.rowcount == 0:
        return (None, 0)
    else:
        return (cursor.fetchall(), cursor.rowcount)

def get_labels_by_ids(cursor, ids):
    """
    Currently returning entire labels set as dict to make this work before prod demo
        { label_id: lablel }
    """
    # labels_query = "SELECT label_id, label from labels where label_id = ANY(%(int)s::int[])"
    labels_query = "SELECT label_id, label FROM labels"

    #  cursor.execute(query_str, (ids))
    cursor.execute(labels_query)

    if cursor.rowcount == 0:
        return {}
    else:
        labels = {}
        for row in cursor:
            labels[row[0]] = row[1]
        return labels
            

def get_results_by_experiment(cursor, ex_id):
    query_str = "SELECT * FROM results WHERE experiment_id = %s"
    cursor.execute(query_str, (ex_id,))
    return cursor.fetchone()


def get_device_info(device_id):
    
    data = {}
    data['done'] = []
    data['running'] = []

    try: 
        conn = get_db()
        cursor = conn.cursor()

        expmnts = get_experiments_by_device(cursor, device_id)
        labels = get_labels_by_ids(cursor, [])

        #print(expmnts[0],expmnts[1])

        if expmnts[1] == 0:
            return data

        for row in expmnts[0]:
            #print(row)
            exp = {}
            exp['id'] = row[0]
            exp['device'] = row[1]

            if (row[2] != None):
                exp['ctrl_start'] = int( float(row[2])*1000 )
            if (row[3] != None):
                exp['ctrl_end'] = int( float(row[3])*1000 )
            exp['ctrl_dur'] = row[4]

            if (row[6] != None):
                exp['test_start'] = int( float(row[5])*1000 )
            if (row[6] != None):
                exp['test_end'] = int( float(row[6])*1000 )
            exp['test_dur'] = row[7]
            exp['fields'] = row[8]
            exp['labels'] = []
            for val in row[9]:
                exp['labels'].append(labels[val])
            exp['graph_path'] = row[10]
            exp['status'] = row[11]
            if exp['status']  in [1,2]:
                data['running'].append(exp)
            elif  exp['status']  in [3,4]:
                exp['result'] = get_results_by_experiment(cursor, row[0])
                data['done'].append(exp)
            else:
                continue

    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)

    # if app.config['DEBUG']:
    #     print(json.dumps(data, default=datetime_handler, indent=1) )

    return data

def get_label_ids(cursor, labels):
    """
    Input - list of strings (labels) max length 32
    Output - list of unique Label IDs associated from labels table

    Used by create_experiment
    """
    query_one = """ INSERT INTO labels (label) VALUES (%s) ON CONFLICT DO nothing; """
    query_two = "select array_agg(label_id) from labels where label=ANY(%s)"

    labs = [(l,) for l in labels]
    cursor.executemany(query_one, labs )
    cursor.execute(query_two, (str_lst2pgarr(labels),) )

    if cursor.rowcount > 0:
        return cursor.fetchall()[0][0]
    else:
        return []
    

def create_experiment_basic(device_id, labels):
    query_str = "INSERT INTO experiments (device_id,ctrl_start, labels, status) VALUES (%s, NOW(), %s, 1)"
    try: 
        conn = get_db()
        cursor = conn.cursor()

        label_ids = get_label_ids(cursor, labels)

        cursor.execute(query_str, (device_id, int_lst2pgarr(label_ids) ) )
        # verify success
        if cursor.rowcount != 1:
            raise DatabaseError('Rowcount error while inserting record',500, {'err_str':str(ex)})
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)


"""
EXPERIMENT STATUS

prod testing    label
  1     5       control
  2     6       testing
  3     7       complete
  4     8       evaluated
  
       15       canceled
"""

def update_experiments(cursor):
    query_str = """
    UPDATE experiments SET status = 2 WHERE ctrl_end < NOW() or ctrl_start+ctrl_dur < NOW();
    UPDATE experiments SET status = 4 WHERE test_end < NOW() or test_start+test_dur < NOW();
    """
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str)
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Error While Updating Experiments", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)



def ex_Test(device_id, experiment_id):
    query_str = " UPDATE experiments SET status = 2, ctrl_end = NOW(), ctrl_dur = NOW()-ctrl_start, test_start = NOW() WHERE device_id = %s AND experiment_id = %s;"
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str, (device_id, experiment_id))
        print(cursor.rowcount)
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)


def ex_Complete(device_id, experiment_id):
    print(device_id, experiment_id, '->', 'complete')
    query_str = " UPDATE experiments SET status = 3, test_end = NOW(), test_dur = NOW()-test_start WHERE device_id = %s AND experiment_id = %s;"
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str, (device_id, experiment_id))
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)


def ex_Evaluate(device_id, experiment_id):
    query_str = " UPDATE experiments SET status = 4 WHERE device_id = %s AND experiment_id = %s;"
    # TODO: ACUTALLY EVALUATE and update RESULTS table
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str, (device_id, experiment_id))
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)


def ex_Cancel(device_id, experiment_id):
    query_str = " UPDATE experiments SET status = 15 WHERE device_id = %s AND experiment_id = %s;"
    try: 
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(query_str, (device_id, experiment_id))
        conn.commit()
        cursor.close()
    except psycopg2.DataError as ex:
        if app.config['DEBUG']:
            print(ex)
        raise InvalidUsage("Malformed Device ID", status_code=400)
    except Exception as ex:
        raise DatabaseError(str(ex), 500)


"""
RESULT STATUS

prod testing    label
 0      4       faulty
 1      5       inconclusive
 2      6       positive
"""

def str_lst2pgarr(alist):
    return '{' + ','.join(alist) + '}'
    
def int_lst2pgarr(alist):
    res  = '{' + ', '.join(str(x) for x in alist) + '}'
    return res
    
#=========================[Form Handling]================================

class Device_Form(FlaskForm):
    device_id = StringField('Device ID', validators=[DataRequired()]) 
    device_api_key = PasswordField('API Key', validators=[DataRequired()])


class Experiment_Form(FlaskForm):
    device_id = StringField('Device ID', validators=[DataRequired()]) 
    device_api_key = PasswordField('API Key', validators=[DataRequired()])
    control_start = None
    experiment_start = None


#============================[ Utils ]===================================
def datetime_handler(x):
    if isinstance(x, datetime.datetime):
        return x.isoformat()
    return x.__str__()
    raise TypeError("Unknown type")

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
