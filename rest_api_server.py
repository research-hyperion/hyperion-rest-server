import flask
from flask import request, jsonify
import sqlite3
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})
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

def get_interaction_pairs_from_list(drug_list):
    interaction_pairs=[]
    for drug1 in drug_list:
        for drug2 in drug_list:
            if drug1==drug2:
                continue
            elif (drug1,drug2) in interaction_pairs or (drug2,drug1) in interaction_pairs:
                continue
            else:
                interaction_pairs.append((drug1,drug2))
    return interaction_pairs
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
    request_data=[]
    if 'list' in request.args:
        drug_list = request.args.getlist('list')
        drug_list = params_to_list(drug_list[0])
        app.logger.warning(drug_list)
        interaction_pairs = []
        if len(drug_list)>=2:
            #prepare interaction pairs
            app.logger.info("Get interaction pairs from drug list {0}".format(drug_list))
            interaction_pairs = get_interaction_pairs_from_list(drug_list)
            app.logger.info("Interaction pairs:{0}".format(interaction_pairs))
            #Check database for interactions
            connection = sqlite3.connect('hyperion.db')
            connection.row_factory = dict_factory
            cursor = connection.cursor()
            for pair in interaction_pairs:
                sql_query = "select drug1name,drug2name,interactioncode from interactions where lower(drug1name) = \'{0}\' and lower(drug2name)=\'{1}\';".format(pair[0],pair[1])
                entry = cursor.execute(sql_query).fetchall()
                app.logger.info(entry)
                if entry:
                    request_data.append(entry[0])
            return jsonify(request_data)
            
        else:
            return "Error: Minimum 2 drugs must be specified!"
    else:
        return "Error: No name field provided!"


    return jsonify(request_data)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404

app.run()
