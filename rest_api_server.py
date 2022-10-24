#!/bin/python3
import flask
import base64
from flask import request, jsonify
import mysql.connector
from mysql.connector import Error
from logging.config import dictConfig

import rest_server_secrets as s

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
app.config["DEBUG"] = False
app.config["PROPAGATE_EXCEPTIONS"]=True

HOST = base64.b64decode(s.HOST).decode("utf-8")
DATABASE = base64.b64decode(s.DATABASE).decode("utf-8")
USER = base64.b64decode(s.USER).decode("utf-8")
PASSWORD = base64.b64decode(s.PASSWORD).decode("utf-8")

SQL_QUERY_SCORE ="(select coalesce(sum(score),0) as score from {0} where (dbid1=\'{3}\' and dbid2=\'{4}\') or (dbid2=\'{3}\' and dbid1=\'{4}\')) union all (select coalesce(sum(score),0) as score from {1} where (dbid1=\'{3}\' and dbid2=\'{4}\') or (dbid2=\'{3}\' and dbid1=\'{4}\')) union all (select coalesce(sum(score),0) as score from {2} where (dbid1=\'{3}\' and dbid2=\'{4}\') or (dbid2=\'{3}\' and dbid1=\'{4}\'))"

#"select score from {0} where (dbid1=\'{1}\' and dbid2=\'{2}\') or (dbid2=\'{1}\' and dbid1=\'{2}\')"

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
    entry = ""
    try:
        connection = mysql.connector.connect(
                host = HOST,
                database = DATABASE,
                user = USER,
                password = PASSWORD)
        if connection.is_connected():
            app.logger.info("Connected to MySql in api handler")
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)
            entry = cursor.fetchall()
            app.logger.info("Selected version from database");
            cursor.close()
            connection.close()
    except Error as e:
        app.logger.error("Error connecting MySQL {0}".format(e))
    finally:
        return jsonify(entry)


@app.route("/api/v1/resources/drugs/all", methods = ['GET'])
def api_all():
    sql_query = "select id, drugname, rodrugname from drugs, rodrugname where drugs.id = rodrugname.drugid;"
    entry = ""
    try:
        connection = mysql.connector.connect(
                host = HOST,
                database = DATABASE,
                user = USER,
                password = PASSWORD)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)
            cursor.execute(sql_query)
            entry = cursor.fetchall()
            cursor.close()
            connection.close()
    except Error as e:
        app.logger.error("Error connecting MySQL {0}".format(e))
    finally:
        return jsonify(entry)

@app.route("/api/v1/resources/scores", methods = ['GET'])
def api_score():
    request_data=[]
    if 'list' in request.args:
        drug_list = request.args.getlist('list')
        drug_list = params_to_list(drug_list[0])
        if len(drug_list)>=2:
            app.logger.info("Scores: get interaction pairs from drug list{0}".format(drug_list))
            interaction_pairs = get_interaction_pairs_from_list(drug_list)
            app.logger.info("Score pairs:{0}".format(interaction_pairs))
            #check db for db id
            try:
                connection = mysql.connector.connect(
                            host = HOST,
                            database = DATABASE,
                            user = USER,
                            password = PASSWORD)
                if connection.is_connected():
                    cursor = connection.cursor(dictionary=True)
                    drug_info = []
                    interval_mild_low = 0;
                    interval_mild_high = (10**(2/3))/2
                    interval_moderate_high = (10**(4/3))/2
                    interval_severe_high = (10**2)/2
                    drugs_map =[]
                    
                    for drug in drug_list:
                        sql_query_drug_id = "select * from drug_score_name_id where drugbankid =\'{0}\';".format(drug)
                        cursor.execute(sql_query_drug_id)
                        drug_id_entry = cursor.fetchall()
                        if drug_id_entry:
                            drugs_map.append({"drugname":drug, "drugid":drug_id_entry[0].get('drugname')})
                        

                    for pair in interaction_pairs:
                        drug_id_1 = ""
                        drug_id_2 = ""
                        for drug_id in drugs_map:
                            if pair[0] == drug_id.get('drugname'):
                                drug_id_1 = drug_id.get('drugid')
                            elif pair[1] == drug_id.get('drugname'):
                                drug_id_2 = drug_id.get('drugid')
                            else:
                                continue
                        drug_info.append((drug_id_1, pair[0], drug_id_2, pair[1])) # drugid1, drugname1, drugid2,drugname2

                    # get the value
                    app.logger.info("Drug info: {0}".format(drug_info))
                    databases = ["drug_score_all_interactions", "drug_score_sm_interactions", "drug_score_s_interactions"]
                    for drug_pair in drug_info:
                        sql_query = SQL_QUERY_SCORE.format(databases[0], databases[1], databases[2], drug_pair[0],drug_pair[2]) 
                        app.logger.info("SQL QUERY:{0}".format(sql_query))
                        
                        cursor.execute(sql_query)
                        entry_db = cursor.fetchall()
                        
                        data_mild = {'low':0, 'medium':0, 'high':0}
                        data_moderate = {'low':0, 'medium':0, 'high':0}
                        data_severe = {'low':0, 'medium':0, 'high':0}
                        app.logger.info("RESULT DB: {0}\t LENGTH:{1}".format(entry_db,len(entry_db))) 
                        if entry_db:
                            value_low = entry_db[0].get('score')
                            value_mod = entry_db[1].get('score')
                            value_high = entry_db[2].get('score')
                            if value_low == 0 and value_mod == 0 and value_high == 0:
                                continue
                            if interval_mild_low <= value_low < interval_mild_high:
                                data_mild['low'] = value_low
                            if interval_mild_high <= value_low < interval_moderate_high:
                                data_mild['medium'] = value_low
                            if interval_moderate_high <= value_low <= interval_severe_high:
                                data_mild['high'] = value_low

                            if interval_mild_low <= value_mod < interval_mild_high:
                                data_moderate['low'] = value_mod
                            if interval_mild_high <= value_mod < interval_moderate_high:
                                data_moderate['medium'] = value_mod
                            if interval_moderate_high <= value_mod <= interval_severe_high:
                                data_moderate['high'] = value_mod

                            if interval_mild_low <= value_high < interval_mild_high:
                                data_severe['low'] = value_high
                            if interval_mild_high <= value_high < interval_moderate_high:
                                data_severe['medium'] = value_high
                            if interval_moderate_high <= value_high <= interval_severe_high:
                                data_severe['high'] = value_high
                                             
                        report_data = {
                                'drugname1':drug_pair[1],
                                'drugname2':drug_pair[3],
                                'dbid1':drug_pair[0],
                                'dbid2':drug_pair[2],
                                'mild_score':data_mild,
                                'moderate_score':data_moderate,
                                'severe_score':data_severe
                        }

                        request_data.append(report_data)
                    cursor.close()
                    connection.close()
            except Error as e:
                app.logger.error("Error connecting MySQL {0}".format(e))
        else:    
            return "Error: Minimum 2 drugs must be specified"
    else:
        return "Error: No name field provided!"
    return jsonify(request_data)


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
            entry = ""
            try:
                connection = mysql.connector.connect(
                            host = HOST,
                            database = DATABASE,
                            user = USER,
                            password = PASSWORD)
                if connection.is_connected():
                    cursor = connection.cursor(dictionary=True)
                    
                    for pair in interaction_pairs:
                        sql_query = "select drug1name,drug2name,interactioncode from interactions where (lower(drug1name) = \'{0}\' and lower(drug2name)=\'{1}\') or (lower(drug1name) = \'{2}\' and lower(drug2name)=\'{3}\');".format(pair[0], pair[1], pair[1], pair[0])
                        cursor.execute(sql_query)
                        entry = cursor.fetchall()
                        app.logger.info(entry)
                        if entry:
                            request_data.append(entry[0])

                    cursor.close()
                    connection.close()
            except Error as e:
                app.logger.error("Error connecting MySQL {0}".format(e))
        else:
            return "Error: Minimum 2 drugs must be specified!"
    else:
        return "Error: No name field provided!"


    return jsonify(request_data)

@app.errorhandler(404)
def page_not_found(e):
    return "<h1>404</h1><p>The resource could not be found.</p>", 404



if __name__ == "__main__":
    app.run(threaded=True, host='0.0.0.0',port=5000)

