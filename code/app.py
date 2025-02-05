"""
Author: Alexander Söderhäll
Date:   17/01/2025

        This class is responsible for the webservers backend logic.
"""
from flask import Flask, render_template, request
from flask_socketio import send, emit, SocketIO
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime, timedelta
import threading
import time


app = Flask(__name__)

# Great functionality that allows one to have configurations in a central place.
load_dotenv
max_results = int(os.getenv("FLASK_MAX_RESULTS"))

# This datastructure (list) holds the most recent RSS feeds. This is used to display 
# "live" RSS data to clients.
live_rss = []

"""
@method Function is run as a separate thread, continously fetches new
        RSS feeds from the SQLite database.
"""
def update_live_rss():
    global live_rss

    update_time = int(os.getenv("FLASK_LIVE_RSS_UPDATE_TIME"))

    while(True):
        result = run_query(query=f"SELECT * FROM rss WHERE fetch_datetime > strftime('%Y/%m/%d %H:%M:%S', 'now', '-4 hour')")
        live_rss = parse_results(result=result)

        time.sleep(update_time)

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
@param  params: Any special parameters that should be used.

@return Returns the query.
"""
def run_query(query: str, params=()):
    con = sqlite3.connect("rss.db")
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    con.close()
    return rows

"""
@method If a client requests the sub-URL /live, return the specified html template.

@return Returns the template live.html
"""
@app.route("/live")
def live():
    return render_template('live.html')

"""
@method If a client requests the sub-URL /get_rss, it means they want the live RSS data.

@return Returns the live RSS data as a JSON object.
"""
@app.route("/get_rss")
def get_rss():
    global live_rss
    test = [{"title": "Test 1", "summary": "This is the first test!", "link": "null", "fetch_datetime": datetime.now().strftime("%Y/%m/%d %H:%M:%S")},
     {"title": "Test 2", "summary": "This is the second test!", "link": "null", "fetch_datetime": (datetime.now() - timedelta(minutes=10)).strftime("%Y/%m/%d %H:%M:%S")}]
    return test

"""
@method If a client requests the top URL, return the "home-page".

@return Returns the template index.html
"""
@app.route("/")
def index():
    result = run_query(query=f"SELECT * FROM rss limit {max_results}")
    parsed_results = parse_results(result=result)
    
    # Flask uses templates to render html.
    # Ref: https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
    return render_template('index.html', results=parsed_results)

# We want the webserver to know of all recent live RSS feeds, start this as a separate thread.
t0 = threading.Thread(target=update_live_rss)
t0.start()