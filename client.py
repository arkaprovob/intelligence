import requests
import json


url = "http://127.0.0.1:8000/query-stream/"


query = {"query": "what is spaship?"}


with requests.post(url, data=json.dumps(query), headers={'Content-Type': 'application/json'}, stream=True) as r:
    for chunk in r.iter_content(1024):
        print(chunk)