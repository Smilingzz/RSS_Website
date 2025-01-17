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
    con.row_factory = sqlite3.Row
    cursor = con.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()
    con.close()
    return rows


@app.route("/")
def index():
    query = f"SELECT * FROM rss limit {max_results}"
    results = run_query(query)
    print(results)
    for result in results:
        title = result[0]
        summary = result[1]
        link = result[2]
        fetch_date = result[3]
        print(result[0])
    # Flask uses templates to render html.
    # Ref: https://flask.palletsprojects.com/en/stable/quickstart/#rendering-templates
    return render_template('index.html', results=results)