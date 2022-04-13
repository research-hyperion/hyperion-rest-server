import flask
from flask import request, jsonify
import sqlite3

app = flask.Flask(__name__)
app.config["DEBUG"] = True

# Database

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def params_to_list(param):
    result = []
    for val in param.split(','):
        if val:
            result.append(val)
    return result
# Routes

@app.route('/', methods = ['GET'])
def home():
    return "<h1>A prototype REST API</h1>"

@app.route("/api/v1/resources/dbversion", methods = ['GET'])
def api_dbversion():
    sql_query = "select * from dbversion;"
    connection = sqlite3.connect('hyperion.db')
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    entry = cursor.execute(sql_query).fetchall()
    return jsonify(entry)


@app.route("/api/v1/resources/drugs/all", methods = ['GET'])
def api_all():
    sql_query = "select * from drugs;"
    connection = sqlite3.connect('hyperion.db')
    connection.row_factory = dict_factory
    cursor = connection.cursor()
    all_database_entries = cursor.execute(sql_query).fetchall()
    return jsonify(all_database_entries)



@app.route("/api/v1/resources/drugs", methods = ['GET'])
def api_name():
    request_data={}
    if 'list' in request.args:
        drug_list = request.args.getlist('list')
        if len(drug_list)==1 and ',' in drug_list[0]:
            request_data['drugs'] = params_to_list(drug_list[0])
        else:
            request_data['drugs'] = drug_list
    else:
        return "Error: No name field provided!"


    return jsonify(request_data)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
