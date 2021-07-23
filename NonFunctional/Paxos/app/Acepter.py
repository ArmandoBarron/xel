#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for
import json
import logging
import sys
import time

logging.basicConfig()
LOG = logging.getLogger()

BRANCHES = dict() #dict of all the REQUEST

app = Flask(__name__)
ACTUAL_VALUE = 0


def save_data(value):
    global BRANCHES
    RN = str(value['control_number'])
    params = value['params']

    if params is None: #the first index
        BRANCHES[RN]=dict()
        BRANCHES[RN]["DAG"]=dict()
    elif params['status'] == "INFO":
        BRANCHES[RN]["DAG"][params['task']]= {'parent':params['parent'],'DAG':params['message']} #save parent of service
    else:
        params['timestamp'] = time.time()
        id_service = params['task']
        BRANCHES[RN][id_service]=params


def consult_data(value):
    global BRANCHES
    RN = str(value['control_number'])
    params = value['params']
    if params is not None: #specific task status
        task = params['task']
        label = BRANCHES[RN][task]['label']
        return {'label':label}
    else: #last update
        task_dict = BRANCHES[RN]
        for key,val in task_dict.items():
            if key=="DAG": #se ignora DAG
                pass
            else:
                #LOG.error(">>>>>>>>>>>>>> %s" % json.dumps(val))
                if val['status']=="RUNNING" and time.time()-val['timestamp'] > 20: #if has passed more than 20 seg of the last health check of one service
                    BRANCHES[RN][key]['status']="ERROR"
                    BRANCHES[RN][key]['message']="Resource %s is not responding. last message: %s." % (val['task'], val['message'])
                    BRANCHES[RN][key]['details']="RESOURCE DOWN"

                if val['status'] == "OK" or val['status']=="ERROR":
                    st =  val['status']
                    BRANCHES[RN][key]['status']="STANDBY" #status stamdby is for a task which already finished and it has been count
                    label = val['label']
                    task = val['task']
                    data_type = val['type']
                    idx_opt = val['index']
                    ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt }
                    if 'details' in val:
                        ToSend['DAG'] =  BRANCHES[RN]["DAG"][key] #{'parent':params['parent'],'DAG':params['message']}
                    return ToSend

        return {'status':"WAITING"}


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


    if action == "PREPARE": #paxos step to reach a consensus
        PV = params['PV']
        if ACTUAL_VALUE < PV:
            ACTUAL_VALUE = PV
            return json.dumps({"status":"OK","action":"PROMISE","PV":ACTUAL_VALUE})
        else:
            return json.dumps({"status":"OK","action":"IGNORE","PV":ACTUAL_VALUE})

    elif action == "ACCEPT": #Accept the request
        PV = params['PV']
        value = params['value']
        if ACTUAL_VALUE == PV:
            #send it to learners
            #response to proposal
            ACTUAL_VALUE =0
            return json.dumps({"status":"OK","action":"ACCEPT","value":value})
        else:
            return json.dumps({"status":"OK","action":"IGNORE","value":value})

    elif action == "SAVE_SOLUTION": #save a new solution
        value = params['value']
        save_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":value})


    elif action == "UPDATE_TASK":
        value = params['value']
        save_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":value})


    elif action == "CONSULT":
        value = params['value']
        res = consult_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    else:
        return {"status":"ERROR"}


    return "Paxos node"
    







if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True)
