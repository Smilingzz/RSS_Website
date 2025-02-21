# Installation 

- Ensure the host running this is using Linux, as Gunicorn is required (do ````sudo apt install gunicorn```).
- Python 3.12.8 was using during development of the code.
- Create a virtual envirnment with ```virtualenv```, do ```virtualenv venv``` followed by ```source venv/bin/activate``` to activate the virtual environment.
- Install Python dependencies with ```python3 -m pip install -r requirements.txt```.
    - In case any fail, inspect the document and install manaully or run any of the scripts to determine which libraries are missing.
- In one terminal, run ```python rss.py```.
- In another terminal, run ```gunicorn app:app```.
- You can now visit localhost ```127.0.0.1:8000``` and search for fetched RSS-streams.
