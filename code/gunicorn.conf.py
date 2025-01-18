import os
from dotenv import load_dotenv

load_dotenv()

workers = int(os.getenv("GUNICORN_PROCESSES"))
threads = int(os.getenv("GUNICORN_THREADS"))
bind = os.getenv("GUNICORN_BIND")

forwarded_allow_ips = "*"
secure_scheme_headers = {"X-Forwarded-Proto": "https"}