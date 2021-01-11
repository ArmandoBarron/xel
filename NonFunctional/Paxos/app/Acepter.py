#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for
import json
import logging
import sys

logging.basicConfig()
LOG = logging.getLogger()

app = Flask(__name__)
ACTUAL_VALUE = 0

@app.route('/')
def prueba():
    return "Paxos node"

@app.route('/health')
def health():
    return json.dumps({'status':'OK'})

@app.route('/REQUEST',methods=['POST'])
def prepare_request():
    global ACTUAL_VALUE


    params = request.get_json(force=True)
    action = params['action']


    if action == "PREPARE":
        PV = params['PV']
        if ACTUAL_VALUE < PV:
            ACTUAL_VALUE = PV
            return json.dumps({"status":"OK","action":"PROMISE","PV":ACTUAL_VALUE})
        else:
            return json.dumps({"status":"OK","action":"IGNORE","PV":ACTUAL_VALUE})

    elif action == "ACCEPT-REQUEST":
        PV = params['PV']
        value = params['value']
        if ACTUAL_VALUE == PV:
            #send it to learners
            #response to proposal
            ACTUAL_VALUE =0
            return json.dumps({"status":"OK","action":"ACCEPT","value":value})
        else:
            return json.dumps({"status":"OK","action":"IGNORE","value":value})

    else:
        return {"status":"ERROR"}


    return "Paxos node"
    







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True)
