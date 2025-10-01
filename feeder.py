# This log takes regex and non regex matching patterns from a log file and ships them to an API logging enpoint named /ingest.
# Change log you wish to open and the rex search if there is one. Otherwise comment out lines 9 and 10 if not searching for a string.

import requests, time, re
f=open('/var/log/auth.log','r',encoding='utf-8',errors='replace'); f.seek(0,2)
url='http://IP:8000/ingest'
rex=re.compile(r'\b(?:\d{1,3}\.){3}\d{1,3}\b')
while True:
    line=f.readline()
    if not rex.search(line):
        continue
    if not line:
        time.sleep(0.2); continue
    try:
        requests.post(url, json={'text': line.rstrip('\n')}, timeout=(2,5))
    except Exception:
        time.sleep(1)
