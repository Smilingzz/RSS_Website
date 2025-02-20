"""
Author: Alexander Söderhäll
Date:   2025-02-17

        This class is responsible for the webservers backend logic and producing the client html 
        that is used to search for data in the SQLite database.
"""
from flask import Flask, render_template, request
import sqlite3
from dotenv import load_dotenv
import os
import json


app = Flask(__name__)

# Great functionality that allows one to have configurations in a central place.
load_dotenv()
max_results = int(os.getenv("FLASK_MAX_RESULTS"))
rss_parameters = json.loads(os.getenv("RSS_PARAMETERS"))
table_name = os.getenv("SQLITE_DB_TABLE_NAME")

"""
@method Given a list of results of the SQLite database, parse the results into a 
        familiar format (dict/json) which can be returned to the client.

@param  result: The list which should be processed.

@return Returns the processed list.
"""
def parse_results(result: list):
    results = []
    for res in result:
        results.append([{"title": res[0], "summary": res[1] if res[1] != "null" else "", "link": res[2], "fetch_date": res[3]}] )
    return results

"""
@method Runs a given query on the SQLite database.

@param  query: A prepared string which should be run on the SQLite database.
@param  params: Any special parameters that should be used, none by default.

@return Returns the query.
"""
def run_query(query: str, params=()):
    con = sqlite3.connect(os.getenv("SQLITE_DB_NAME"))
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    con.close()
    return rows

"""
@method Queries the SQLite database for a search word that the client has transmitted to the server.
        Returns all matching entries inside the SQLite database to the client.

@param  search: The search string that the user has entered.

@return Returns the rendered HTML template.
"""
@app.route("/fetch_rss")
def fetch_rss():
    global rss_parameters, table_name
    search = request.args.get("rss_search")
    built_query_condition = ""
    for parameter in rss_parameters:
        if built_query_condition == "":
            built_query_condition = f"WHERE {parameter} like '%{search}%' or "
        else:
            built_query_condition = built_query_condition + f"{parameter} like '%{search}%' or "
    built_query_condition = built_query_condition[0:-3]
    result = run_query(query=f"SELECT * FROM {table_name} {built_query_condition}")

    return render_template('index.html', results=parse_results(result))

"""
@method If a client requests the top URL, return the "home-page".

@return Returns the template index.html
"""
@app.route("/")
def index():
    global table_name
    result = run_query(query=f"SELECT * FROM {table_name} limit {max_results}")
    
    # Flask uses templates to render html.
    # Ref: https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
    return render_template('index.html', results=parse_results(result=result))