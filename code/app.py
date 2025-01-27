"""
Author: Alexander Söderhäll
Date:   17/01/2025

        This class is responsible for the webservers backend logic.
"""
from flask import Flask, render_template, request
import sqlite3
from dotenv import load_dotenv
import os
from datetime import datetime
import threading
import time


app = Flask(__name__)


load_dotenv
max_results = int(os.getenv("FLASK_MAX_RESULTS"))

# This datastructure (list) holds the most recent RSS feeds. This is used to display 
# "live" RSS data to clients.
live_rss = []


def update_live_rss():
    global live_rss

    update_time = int(os.getenv("FLASK_LIVE_RSS_UPDATE_TIME"))

    while(True):
        result = run_query(query=f"SELECT * FROM rss WHERE fetch_datetime > strftime('%Y/%m/%d %H:%M:%S', 'now', '-4 hour')")
        live_rss = parse_results(result=result)

        time.sleep(update_time)


def parse_results(result: list):
    results = []
    for res in result:
        results.append([{"title": res[0], "summary": res[1] if res[1] != "null" else "", "link": res[2], "fetch_date": res[3]}] )
    return results


def run_query(query, params=()):
    con = sqlite3.connect("rss.db")
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    con.close()
    return rows


@app.route("/live")
def live():
    return render_template('live.html')


@app.route("/get_rss")
def live():
    global live_rss

    return render_template('live.html', results=live_rss)


@app.route("/")
def index():
    result = run_query(query=f"SELECT * FROM rss limit {max_results}")
    parsed_results = parse_results(result=result)
    
    # Flask uses templates to render html.
    # Ref: https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
    return render_template('index.html', results=parsed_results)


t0 = threading.Thread(target=update_live_rss)
t0.start()