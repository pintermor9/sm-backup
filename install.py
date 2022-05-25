# WIP


import requests
import os


resp = requests.get(
    "https://raw.githubusercontent.com/pintermor9/sm-backup/main/main.py"
)

with open(os.path.expanduser("~\\pintermor9\\sm-backup\\main\\main.py"), "w", encoding="utf-8") as f:
    f.write(resp.text)
