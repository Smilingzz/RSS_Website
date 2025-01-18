"""
Author: Alexander Söderhäll
Date:   17/01/2025

        This class is responsible for the webservers backend logic.
"""
from flask import Flask, render_template, request
import sqlite3
from dotenv import load_dotenv
import os


app = Flask(__name__)


load_dotenv





max_results = int(os.getenv("FLASK_MAX_RESULTS"))


def run_query(query, params=()):
    con = sqlite3.connect("rss.db")
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    con.close()
    return rows

""" @app.route("/live")
def live():
    result = run_query(query=f"") """


@app.route("/")
def index():
    result = run_query(query=f"SELECT * FROM rss limit {max_results}")
    results = []
    for res in result:
        results.append([{"title": res[0], "summary": res[1] if res[1] != "null" else "", "link": res[2], "fetch_date": res[3]}] )
    
    # Flask uses templates to render html.
    # Ref: https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
    return render_template('index.html', results=results)