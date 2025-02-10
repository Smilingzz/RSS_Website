"""
Author: Alexander Söderhäll
Date: 2025-01-14

This task is the so called "gesällprov" in course IPROG at SU. 

The program designed fetches RSS feeds, parses and stores them in a SQLite database. 
The SQLite database is then used to train a GPT model which can be interacted with to ask questions 
regarding the data. For example, "What are some big recent news stories?", in which the GPT model
will answer accordingly.

The program uses multi-threading and databases, learned in the course.
"""
import os
import subprocess
from dotenv import load_dotenv
import time
import feedparser
import sqlite3
import threading
import queue
import json
import datetime
from flask import Flask, render_template, request
import regex as re

# Global variables
q = queue.Queue()


"""
@method Main method of the program.
        Initialize the SQLite server and start two threads.
        One thread should fetch and parse SS feeds, the other should upload and communicate with the SQLite server.
"""
def main():


    # .env contains variables used in the program.
    load_dotenv()


    # Start a thread which fetches RSS feeds.
    t0 = threading.Thread(target=rss_parser().fetch_feeds)
    t0.daemon = True
    t0.start()


    # Start a thread which updates the SQLite database with fresh RSS feeds.
    t1 = threading.Thread(target=SQLite_handler().update_SQLite)
    t1.daemon = True
    t1.start()
    

    # Since we're allowing the threads to exit once the main thread exists, ensure main thread does not exit.
    # Mainly done during production, to ensure process can be killed easily.
    while True:
        time.sleep(1)


"""
@class  This class is responsible for fetching RSS feeds. It adds any found RSS feeds to the shared rss_set buffer.
"""
class rss_parser():


    """
    @constructor    Instantiate the rss_parser object, read from .env the frequency which the RSS feeds should be checked
                    and from what URLs it should look for RSS feeds.
    """
    def __init__(self):
        self.fetch_frequency = int(os.getenv("RSS_UPDATE_FREQUENCY"))
        self.feeds = json.loads(os.getenv("RSS_FEEDS"))
        self.rss_parameters = json.loads(os.getenv("RSS_PARAMETERS"))
        self.url_feed = {}

        # In case some feeds to not work, stop from fetching them for some time.
        self.no_update_loops = int(os.getenv("RSS_NO_FEED_LOOP"))
        self.error_feed = {}
        self.error_loops = {}
        for url in self.feeds:
            self.url_feed[url] = None
            self.error_feed[url] = False
            self.error_loops[url] = 0


    """
    @method Given a fetched feed (HTTP 200), parse some common items and add to the message queue.
            The SQLite thread will then add (if unique/new) to the SQLite database.
    """
    def parse_and_send_feed(self, feed):
        for item in feed.entries:
            new_entry = {}
            for key in self.rss_parameters:
                new_entry[key] = "null"
            new_entry["fetch_datetime"] = datetime.datetime.now().strftime("%Y/%m/%d %H:%M:%S")
            for key in item:
                if key in self.rss_parameters:
                    new_entry[key] = item[key]
            q.put(new_entry)

    
    """
    @method At a given interval, fetch RSS feeds from the given urls.
            Parse them and extract wanted information, add them to the shared buffer.
    """
    def fetch_feeds(self):
        while(True):
            for url in self.feeds:
                if self.error_feed[url]:
                    if self.error_loops[url] == 10:
                        self.error_feed[url] = False
                    else:
                        self.error_loops[url] += 1
                    continue
                # Ensure we're only parsing new data. Status code 304 if there are no updates.
                # Ref: https://feedparser.readthedocs.io/en/stable/http-etag.html#http-etag
                feed = self.url_feed[url] = feedparser.parse(url)
                if feed.status == 200:
                    self.parse_and_send_feed(feed)
                else:
                    print("Error:", feed.status, "Could not parse url:", url)
                    self.error_feed[url] = True
                    self.error_loops[url] = 0

            time.sleep(self.fetch_frequency)


"""
@class  This class is responsible for ensure the SQLite server is running and is configured.
        It is also responsible for adding new RSS feeds to the SQLite server.

        If there's any errors with the database, simply delete "rss.db" in the same folder as this.
        This will prompt the code to initialize a new, empty, database.
"""
class SQLite_handler():


    """
    @constructor    Instantiate the SQLite_handler object, read the frequency (in seconds) which the database should be updated 
                    with new RSS feeds.
    """
    def __init__(self):
        self.SQLite_update_frequency = int(os.getenv("SQLITE_UPDATE_FREQUENCY"))
        self.html_parser = re.compile("<.*>")
        self.table_name = os.getenv("SQLITE_DB_TABLE_NAME")
        self.rss_parameters = json.loads(os.getenv("RSS_PARAMETERS"))
        self.query_parameters = ", ".join(self.rss_parameters) + ", fetch_datetime"
        self.query_length = ", ".join(["?" for _ in range(len(self.rss_parameters)+1)])


    """
    @method Frequently check if new RSS feeds have been added.
            If so, add them to the SQLite database table and remove them from the buffer.
    """
    def update_SQLite(self):
        con = sqlite3.connect(os.getenv("SQLITE_DB_NAME"))
        self.db_cursor = con.cursor()
        parameters = "(" + " text, ".join(self.rss_parameters) + " text, fetch_datetime text, " + "UNIQUE(" + ",".join(self.rss_parameters) + ",fetch_datetime))"
        self.db_cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name}{parameters}")
        #self.db_cursor.execute(f"CREATE TABLE IF NOT EXISTS {self.table_name}(title text, summary text, link text, fetch_datetime text, UNIQUE(title, summary, link, fetch_datetime))")
        while(True):
            entry = q.get()
            self.add_SQLite_entry(entry)
            #print(entry)
            time.sleep(self.SQLite_update_frequency)
    

    """
    @method Add an entry to the SQLite database.
            Since a row must be unique, only new entries are successfully added.
    """
    def add_SQLite_entry(self, entry: tuple):
        if self.html_parser.match(entry["title"]) or self.html_parser.match(entry["summary"]):
            return
        title = entry["title"]
        summary = entry["summary"]
        link = entry["link"]
        date = entry["fetch_datetime"]
        #print(self.query_parameters)
        #print(self.query_length)
        command = f"INSERT OR IGNORE INTO {self.table_name} ({self.query_parameters}) VALUES({self.query_length})"
        self.db_cursor.execute(command, (title, summary, link, date))
        self.db_cursor.connection.commit()

main()