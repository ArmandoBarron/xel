#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for
import json
import logging
import sys
import time
import datetime

import hashlib
from datetime import datetime
from db_handler import Handler

logging.basicConfig()
LOG = logging.getLogger()
BRANCHES = dict() #dict of all the REQUEST

app = Flask(__name__)
ACTUAL_VALUE = 0



"""
{
    "token_solution":{
        token_solution:""
        last_update:"",
        DAG:[],
        metadata:{name:"",desc:"",tags:[],frontend:""},
        task_list: {
            <task>:
                    {
                    label,
                    data_type,
                    parent,
                    status:,
                    fingerprint:,
                    messsage:,
                    historic:[{status,message,timestamp}]
                    last_update:
                    }
            }
    }
}

"""

def GetCurrentTimeAction():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")

def Create_fingerprint(string_data):
    encoded=string_data.encode()
    result = hashlib.sha256(encoded).hexdigest()
    return result

def Compare_fingerprints(fp1,fp2):
    if(fp1==fp2):
        return True
    else:
        return False

def LookForParams(DAG,task):
    params = None
    for bb in DAG:
        LOG.error("encuenta esto %s " %bb['id'])
        if bb['id'] == task:
            LOG.error("<<<<<<<<<<<<<<<<<<< LO ENCONTO <<<<<<<<<<<<<<<<<<<<<<<<< %s " %task)
            params = bb
            break
        else:
            if 'childrens' not in bb:
                bb['childrens']=[]
            params = LookForParams(bb['childrens'],task) # look  by children
            if params is not None:
                break
    LOG.error(params)
    return params


def update_data(value): #called on bb report
    global BRANCHES
    RN = value['control_number']
    params = value['params']
    time_action = GetCurrentTimeAction()

    LOG.error(value['params'])
    if params['task'] not in BRANCHES[RN]["task_list"]: 
        BRANCHES[RN]["task_list"][params['task']]=dict()
        BRANCHES[RN]["task_list"][params['task']]['historic']=[]
        BRANCHES[RN]["task_list"][params['task']]['parent']=''
        dag = LookForParams(BRANCHES[RN]["DAG"], params['task']) #look for the params of the task to create a fingerprint (if params are dfiferrent then the task is not the same)
        BRANCHES[RN]["task_list"][params['task']]['fingerprint']=Create_fingerprint(json.dumps(dag['params']))

    BRANCHES[RN]["task_list"][params['task']]['data_type'] = params['type']
    BRANCHES[RN]["task_list"][params['task']]['label'] = params['label']
    BRANCHES[RN]["task_list"][params['task']]['index'] = params['index']
    BRANCHES[RN]["task_list"][params['task']]['status'] = params['status']
    BRANCHES[RN]["task_list"][params['task']]['message'] = params['label']
    BRANCHES[RN]["task_list"][params['task']]['historic'].append({'status':params['status'],'message':params['message'],'timestamp':time_action})
    BRANCHES[RN]["task_list"][params['task']]['last_update'] = time_action
    BRANCHES[RN]["task_list"][params['task']]['timestamp'] = time.time()

    if 'parent' in params:
        if params['parent'] != '':
            BRANCHES[RN]["task_list"][params['task']]['parent'] = params['parent']


def update_task_status(RN,task,status,message,details=None): #called on monitoring 
    global BRANCHES
    time_action = GetCurrentTimeAction()
    BRANCHES[RN]['task_list'][task]['status']=status
    BRANCHES[RN]['task_list'][task]['message']=message
    BRANCHES[RN]['task_list'][task]['last_update']=time_action
    BRANCHES[RN]['last_update']=time_action #update solution status
    BRANCHES[RN]['task_list'][task]['timestamp']= time.time()

    if details is not None:
        BRANCHES[RN]['task_list'][task]['details']=details
    BRANCHES[RN]['task_list'][task]['historic'].append({'status':status,'message':message,'timestamp':time_action})

def Get_solution_if_exist(token_solution,auth):
    global BRANCHES
    solution = None
    SDB=Handler()
    if token_solution in BRANCHES:
        solution = BRANCHES[token_solution]
    elif SDB.Document_exist(auth['user'],token_solution):
        solution = SDB.Get_document(auth['user'],token_solution)
        BRANCHES[token_solution]=solution
    return solution

def validate_solution(dag, solution,token_solution,parent=''):
    global BRANCHES
    #compare dag with task list in the solution
    new_dag=[]
    for taskInDag in dag:
        if 'childrens' not in taskInDag:
            taskInDag['childrens']=[]
        childrens = taskInDag['childrens']
        id_service =taskInDag['id']
        params =json.dumps(taskInDag['params'])
        fp_dag = Create_fingerprint(params)

        if id_service in solution['task_list']:

            taskInSolution = solution['task_list'][id_service]
            Fingerprints_comparation = Compare_fingerprints(taskInSolution['fingerprint'],fp_dag)
            LOG.error("LA COMPARACION DE FP ES %s para la tarea %s con status %s" %(Fingerprints_comparation,id_service,taskInSolution['status']))

            if (Fingerprints_comparation and taskInSolution['status']=="FINISHED"):
                #validate status and fingerprints
                BRANCHES[token_solution]["task_list"][id_service]['status']="OK" #update status. since has finished
                children_dag = validate_solution(childrens,solution,token_solution,parent=id_service)
                for x in children_dag:
                    new_dag.append(x)
            else:
                new_dag.append(taskInDag)
                BRANCHES[token_solution]["task_list"][id_service]['status']="STARTING" #update status. since it will be executed again 

        else: #it is new
            #must be registred in the task list 
            time_action = GetCurrentTimeAction()
            BRANCHES[token_solution]["task_list"][id_service]=dict()
            BRANCHES[token_solution]["task_list"][id_service]['historic']=[]
            BRANCHES[token_solution]["task_list"][id_service]['parent']=parent
            BRANCHES[token_solution]["task_list"][id_service]['fingerprint']=fp_dag

            BRANCHES[token_solution]["task_list"][id_service]['data_type'] = ''
            BRANCHES[token_solution]["task_list"][id_service]['label'] = ''
            BRANCHES[token_solution]["task_list"][id_service]['index'] = ''
            BRANCHES[token_solution]["task_list"][id_service]['status'] = 'STARTING'
            BRANCHES[token_solution]["task_list"][id_service]['message'] = 'NEW SERVICE ADDED.. STARTING EXECUTION.'
            BRANCHES[token_solution]["task_list"][id_service]['last_update'] = time_action
            BRANCHES[token_solution]["task_list"][id_service]['timestamp'] = time.time()

            new_dag.append(taskInDag)

    return new_dag

    for task in solution['task_list']:
        task_status = task['status']
        task_fingerprint = task['fingerprint']




def save_data(value):
    """
    Save metadata in memory.
    Prepares everithing for the execution.
    """
    global BRANCHES
    RN = str(value['control_number'])
    dag = value['DAG']
    auth = value['auth']
    LOG.error(auth)
    LOG.error(type(auth))
    #options = value['exe_opt']
    force = False

    solution =  Get_solution_if_exist(RN,auth)
    if (force is False) and solution!=None:
        new_dag = validate_solution(dag,solution,RN)
        BRANCHES[RN]["DAG"]=dag
        BRANCHES[RN]["last_update"]=GetCurrentTimeAction()
        dag = new_dag

    else:
        BRANCHES[RN]=dict()
        BRANCHES[RN]["DAG"]=dag
        BRANCHES[RN]["token_solution"]=RN
        BRANCHES[RN]["task_list"]=dict()
        BRANCHES[RN]["last_update"]=GetCurrentTimeAction()
        #BRANCHES[RN]["metadata"]=dict()

    return {"DAG":dag,"task_list":BRANCHES[RN]["task_list"]}


def store_data(value):
    """
    Save metadata in DB.
    """
    global BRANCHES

    RN = str(value['control_number'])
    dag = value['DAG']
    meta = value['metadata'] #{name:"",desc:"",tags:[],frontend:""}
    auth = value['auth'] 


    if RN in BRANCHES:     #get updated info from memory
        last_up = BRANCHES[RN]["last_update"]
        task_l = BRANCHES[RN]["task_list"]
    else: #if not in memory, search in DB
        last_up = GetCurrentTimeAction() 
        task_l = []

    solution = {
                "token_solution":RN,
                "last_update":last_up,
                "DAG":dag,
                "metadata":meta,
                "task_list": task_l
            }
    SDB = Handler() 
    SDB.Update_document(auth['user'],RN,solution)

    return ""

def retrieve_solution(value):
    global BRANCHES
    auth = value['auth'] 
    RN = value['control_number']
    SDB = Handler() 
    sol_to_user = SDB.Get_document(auth['user'],RN)
    return sol_to_user


def list_solutions(value):
    global BRANCHES
    auth = value['auth'] 
    SDB = Handler() 
    list_solutions_of_user = SDB.List_document(auth['user'])
    return list_solutions_of_user



def consult_data(value):
    global BRANCHES
    RN = str(value['control_number'])
    params = value['params']

    if params is not None: #specific task status to get data
        task = params['task']
        label = BRANCHES[RN]['task_list'][task]['label'] 
        return BRANCHES[RN]['task_list'][task] #{'label':label}
    else: #last update
        for key,val in BRANCHES[RN]['task_list'].items():

            if val['status']=="RUNNING" and time.time()-val['timestamp'] > 20: #if has passed more than 20 seg of the last health check of one service
                update_task_status(RN,key,"ERROR","Resource %s is not responding. last message: %s." % (key, val['message']),details="RESOURCE DOWN")

            if val['status'] == "OK":
                LOG.error(val)

                st =  val['status']
                label = val['label']
                task = key
                data_type = val['data_type']
                idx_opt = val['index']

                ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt }
                update_task_status(RN,key,"FINISHED","Execution completed without errors")

                return ToSend

            if val['status']=="ERROR":
                st =  val['status']
                label = val['label']
                task = key
                data_type = val['data_type']
                idx_opt = val['index']
                
                ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt }
                update_task_status(RN,key,"FAILED",val['message'])

                if 'details' in val: #this mean that the resource failed, so its secure to recover try to recover data
                    dag = LookForParams(BRANCHES[RN]["DAG"],task)
                    ToSend['DAG'] =  dag 
                    ToSend['parent'] =  val['parent'] 
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
        res = save_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "STORE_SOLUTION": #save a new solution in DB
        value = params['value']
        res = store_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "RETRIEVE_SOLUTION": #save a new solution
        value = params['value']
        res = retrieve_solution(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "LIST_SOLUTIONS": #save a new solution
        value = params['value']
        res = list_solutions(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})
    
    elif action == "UPDATE_TASK":
        value = params['value']
        update_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":value})


    elif action == "CONSULT":
        value = params['value']
        res = consult_data(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    else:
        return {"status":"ERROR","value":"Something happend"}








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True)
