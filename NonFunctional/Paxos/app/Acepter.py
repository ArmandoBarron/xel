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
from TwoChoices import loadbalancer

logging.basicConfig()
LOG = logging.getLogger()
BRANCHES = dict() #dict of all the REQUEST

app = Flask(__name__)
ACTUAL_VALUE = 0

with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services
LOAD_B = loadbalancer(dictionary)


"""
{
    "token_solution":{
        token_solution:""
        last_update:"",
        status:"RUNNING",
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
    if params['task'] not in BRANCHES[RN]["task_list"]: # if the task is new we create a new fingerprint
        BRANCHES[RN]["task_list"][params['task']]=dict()
        BRANCHES[RN]["task_list"][params['task']]['historic']=[]
        BRANCHES[RN]["task_list"][params['task']]['parent']=''
        dag = LookForParams(BRANCHES[RN]["DAG"], params['task']) #look for the params of the task to create a fingerprint (if params are dfiferrent then the task is not the same)
        BRANCHES[RN]["task_list"][params['task']]['fingerprint']=Create_fingerprint(json.dumps(dag['params']))
        

    BRANCHES[RN]["task_list"][params['task']]['data_type'] = params['type']
    BRANCHES[RN]["task_list"][params['task']]['label'] = params['label']
    BRANCHES[RN]["task_list"][params['task']]['index'] = params['index']
    BRANCHES[RN]["task_list"][params['task']]['is_recovered']=False
    BRANCHES[RN]["task_list"][params['task']]['status'] = params['status']
    BRANCHES[RN]["task_list"][params['task']]['message'] = params['message']
    BRANCHES[RN]["task_list"][params['task']]['historic'].append({'status':params['status'],'message':params['message'],'timestamp':time_action})
    BRANCHES[RN]["task_list"][params['task']]['last_update'] = time_action
    BRANCHES[RN]["task_list"][params['task']]['timestamp'] = time.time()

    if 'parent' in params:
        if params['parent'] != '':
            BRANCHES[RN]["task_list"][params['task']]['parent'] = params['parent']

def update_solution_status(token_solution,status):
    global BRANCHES
    BRANCHES[token_solution]["last_update"]=GetCurrentTimeAction()
    BRANCHES[token_solution]["status"] = status

def update_task_status(RN,task,status,message,details=None,is_recovered = False, fingerprint=None): #called on monitoring 
    global BRANCHES
    time_action = GetCurrentTimeAction()
    BRANCHES[RN]['task_list'][task]['status']=status
    BRANCHES[RN]['task_list'][task]['message']=message
    BRANCHES[RN]['task_list'][task]['last_update']=time_action
    BRANCHES[RN]['last_update']=time_action #update solution status
    BRANCHES[RN]['task_list'][task]['timestamp']= time.time()

    if (is_recovered):
        BRANCHES[RN]['task_list'][task]['is_recovered'] = is_recovered

    if fingerprint is not None:
        BRANCHES[RN]["task_list"][task]['fingerprint']=fingerprint  # The fingerprint changed, so we save the new one

    if details is not None:
        BRANCHES[RN]['task_list'][task]['details']=details
    BRANCHES[RN]['task_list'][task]['historic'].append({'status':status,'message':message,'timestamp':time_action})

def Get_solution_if_exist(token_solution,auth):
    global BRANCHES
    solution = None
    SDB=Handler()
    if token_solution in BRANCHES:
        solution = BRANCHES[token_solution]
        LOG.error("==============> recuperando datos de memoria")
    elif SDB.Document_exist(auth['user'],token_solution):
        solution = SDB.Get_document(auth['user'],token_solution)
        BRANCHES[token_solution]=solution
        LOG.error("==============> recuperando datos de la BD")
    return solution

def GetSolutionData(token_project,token_solution): #this function will replace Get_solution_if_exist() in the future
    global BRANCHES
    solution = None
    SDB=Handler()
    if token_solution in BRANCHES:
        solution = BRANCHES[token_solution]
        LOG.error("==============> recuperando datos de memoria")
    elif SDB.Document_exist(token_project,token_solution):
        solution = SDB.Get_document(token_project,token_solution)
        BRANCHES[token_solution]=solution
        LOG.error("==============> recuperando datos de la BD")
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
                update_task_status(token_solution,id_service,"OK","Task has no changes",is_recovered = True)
                #BRANCHES[token_solution]["task_list"][id_service]['status']="OK" #update status. since has finished
                
                children_dag = validate_solution(childrens,solution,token_solution,parent=id_service)
                for x in children_dag:
                    new_dag.append(x)
            else:
                new_dag.append(taskInDag)
                update_task_status(token_solution,id_service,"STARTING","Task has changes",fingerprint=fp_dag )
                #BRANCHES[token_solution]["task_list"][id_service]['status']="STARTING" #update status. since it will be executed again 
                


        else: #it is new
            #must be registred in the task list 
            time_action = GetCurrentTimeAction()
            #if not 'task_list' in BRANCHES[token_solution]:
            #    BRANCHES[token_solution]["task_list"]=dict()
            #LOG.error(BRANCHES[token_solution]["task_list"])

            BRANCHES[token_solution]["task_list"][id_service]=dict()
            BRANCHES[token_solution]["task_list"][id_service]['historic']=[]
            BRANCHES[token_solution]["task_list"][id_service]['parent']=parent
            BRANCHES[token_solution]["task_list"][id_service]['fingerprint']=fp_dag
            BRANCHES[token_solution]["task_list"][id_service]['is_recovered']=False
            BRANCHES[token_solution]["task_list"][id_service]['data_type'] = ''
            BRANCHES[token_solution]["task_list"][id_service]['label'] = ''
            BRANCHES[token_solution]["task_list"][id_service]['index'] = ''
            BRANCHES[token_solution]["task_list"][id_service]['status'] = 'STARTING'
            BRANCHES[token_solution]["task_list"][id_service]['message'] = 'NEW SERVICE ADDED.. STARTING EXECUTION.'
            BRANCHES[token_solution]["task_list"][id_service]['last_update'] = time_action
            BRANCHES[token_solution]["task_list"][id_service]['timestamp'] = time.time()

            new_dag.append(taskInDag)

    return new_dag





def save_data(value):
    """
    Save metadata in memory.
    Prepares everithing for the execution.
    """
    global BRANCHES
    RN = str(value['control_number'])
    dag = value['DAG']
    auth = value['auth']

    #options = value['exe_opt']
    force = False
    is_already_running=False
    solution =  Get_solution_if_exist(RN,auth)
    if (force is False) and solution!=None:
        if "status" not in BRANCHES[RN]: #esto es temporal, para que las soliciones que yae sten guardadas no tengan problemas
            BRANCHES[RN]['status']="FINISHED"

        LOG.error("====== STATUS DE LA SOLUCION ======")
        LOG.error(BRANCHES[RN]['status'])
        if BRANCHES[RN]["status"]!="RUNNING": # if solution is already running
            new_dag = validate_solution(dag,solution,RN)
            BRANCHES[RN]["DAG"]=dag        
            dag = new_dag
            update_solution_status(RN,"RUNNING")
        else:
            is_already_running=True
    else:
        BRANCHES[RN]=dict()
        BRANCHES[RN]["DAG"]=dag
        BRANCHES[RN]["token_solution"]=RN
        BRANCHES[RN]["task_list"]=dict()
        update_solution_status(RN,"RUNNING")

    return {"DAG":dag,"task_list":BRANCHES[RN]["task_list"],"is_already_running":is_already_running}


def store_data(value):
    """
    Save metadata in DB.
    """
    global BRANCHES

    RN = str(value['control_number'])
    dag = value['DAG']
    meta =value['metadata'] #{name:"",desc:"",tags:[],frontend:""}
    auth = value['auth'] 


    if RN in BRANCHES:     #get updated info from memory
        last_up = BRANCHES[RN]["last_update"]
        task_l = BRANCHES[RN]["task_list"]
    else: #if not in memory, search in DB
        last_up = GetCurrentTimeAction() 
        task_l = {}

    solution = {
                "token_solution":RN,
                "last_update":last_up,
                "DAG":dag,
                "metadata":meta,
                "task_list": task_l
            }
    LOG.error(type(meta))

    SDB = Handler() 
    SDB.Update_document(auth['user'],RN,solution)

    return ""

def delete_solution(value):
    auth = value['auth'] 
    RN = value['control_number']
    SDB = Handler() 
    SDB.Delete_document(auth['user'],RN)

    if SDB.Document_exist(auth['user'],RN):
        return {"status":"ERROR","message":"Solution could not be removed"}
    else:
        return {"status":"OK","message":"Solution removed sucessfully"}
    
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




def get_task_runtime_info(value): #new version of consult data
    RN = str(value['control_number'])
    token_project = str(value['token_project'])
    list_info={}

    solution = GetSolutionData(token_project,RN) # solution has a copy of the info in the current timestamp. 

    n_task = len(solution['task_list'])

    count_ok_task=0
    count_error_task=0
    for task,val in solution['task_list'].items():
        ToSend = {'status':"WAITING"}
        if val['status']=="RUNNING" and time.time()-val['timestamp'] > 20: #if has passed more than 20 seg of the last health check of one service
            update_task_status(RN,task,"ERROR","Resource %s is not responding. last message: %s." % (task, val['message']),details="RESOURCE DOWN")

        if val['status'] == "FINISHED" or val['status'] == "FAILED"  or val['status'] == "RUNNING":
            st =  val['status']
            data_type = val['data_type']
            idx_opt = val['index']
            is_recovered = val['is_recovered']
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            if val['status'] != "RUNNING":
                count_ok_task+=1
        
        if val['status'] == "OK":
            st =  val['status']
            data_type = val['data_type']
            idx_opt = val['index']
            is_recovered = val['is_recovered']
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            count_ok_task+=1
            update_task_status(RN,task,"FINISHED","Execution completed without errors")

        if val['status']=="ERROR":
            st =  val['status']
            data_type = val['data_type']
            idx_opt = val['index']
            is_recovered = val['is_recovered']
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            count_error_task+=1
            update_task_status(RN,task,"FAILED",val['message'])

            if 'details' in val: #this mean that the resource failed, so its secure to recover try to recover data
                ToSend['DAG'] =  LookForParams(solution["DAG"],task) 
                ToSend['parent'] =  val['parent'] 
        


        list_info[task]=ToSend
    
    if count_ok_task+count_error_task==n_task:
        if count_error_task>0:
            update_solution_status(RN,"FAILED")
        else:
            update_solution_status(RN,"FINISHED")



    return list_info

def consult_data(value):
    global BRANCHES
    RN = str(value['control_number'])
    params = value['params']

    if params is not None: #specific task status to get data
        task = params['task']
        return BRANCHES[RN]['task_list'][task] #{'label':label}
    else: #last update
        for task,val in BRANCHES[RN]['task_list'].items():

            if val['status']=="RUNNING" and time.time()-val['timestamp'] > 20: #if has passed more than 20 seg of the last health check of one service
                update_task_status(RN,task,"ERROR","Resource %s is not responding. last message: %s." % (task, val['message']),details="RESOURCE DOWN")

            if val['status'] == "OK":
                st =  val['status']
                label = val['label']
                data_type = val['data_type']
                idx_opt = val['index']

                ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt }
                update_task_status(RN,task,"FINISHED","Execution completed without errors")

                return ToSend

            if val['status']=="ERROR":
                st =  val['status']
                label = val['label']
                data_type = val['data_type']
                idx_opt = val['index']
                
                ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt }
                update_task_status(RN,task,"FAILED",val['message'])

                if 'details' in val: #this mean that the resource failed, so its secure to recover try to recover data
                    ToSend['DAG'] =  LookForParams(BRANCHES[RN]["DAG"],task) 
                    ToSend['parent'] =  val['parent'] 
                return ToSend

        return {'status':"WAITING"}



def ResourcesManagment(action,value):
    """
    value {
        action
        action_params{service,service_id,context}
        data_bin
    }
    """
    action = value['action']
    action_params = value['action_params']
    data_bin = value['data_bin']

    service = action_params['service']
    service_id = action_params['service_id']
    
    if action=="ADD":
        status = LOAD_B.Addresource(service,service_id,data_bin)
        if status:
            LOG.info("REGISTRED %s, ip:%s" % (service,service_id))
        else:
            LOG.info("ALREADY REGISTRED %s, ip:%s" % (service,service_id))
        res = {'status':'OK'}
    elif action=="DISABLE":#when a node is down
        LOAD_B.NodeDown(service,service_id)
        res = {'status':'OK'}
    elif action=="ADD_WORKLOAD":#add workload
        LOAD_B.AddWorkload(service,service_id,n=1)
        res = {'status':'OK'}

    ## READ ACTIONS
    elif action=="STATUS":#add workload
        res=LOAD_B.GetStatus()
    elif action=="SELECT":#select a resource
        res= LOAD_B.decide(service, action_params['context']) #search services in the same context

    return res








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

    elif action == "DELETE_SOLUTION": #save a new solution
        value = params['value']
        res = delete_solution(value)
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

    elif action == "CONSULT_V2":
        value = params['value']
        res  = get_task_runtime_info(value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "RESOURCES":
        value = params['value']
        res = ResourcesManagment(value['action'],value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    else:
        return {"status":"ERROR","value":"Something happend"}








if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True)
