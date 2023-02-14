#!/usr/bin/env python3.7
from flask import Flask
from flask import request, url_for
import json
import logging
import sys
import time
import datetime
import copy
from waitress import serve
import multiprocessing as mp

import hashlib
from datetime import datetime
from db_handler import Handler
from TwoChoices import loadbalancer

logging.basicConfig(level=logging.INFO)
LOG = logging.getLogger()

#fh = logging.FileHandler('errors.log')
#fh.setLevel(logging.ERROR)
#LOG.addHandler(fh)

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
                    last_update:,
                    dag #NEW
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

def Compare_parents(parent1,parent2):
    if(parent1==parent2):
        return True
    else:
        return False


def LookForParams(DAG,task):
    params = None
    for bb in DAG:
        #LOG.error("encuenta esto %s " %bb['id'])
        if bb['id'] == task:
            params = bb
            break
        else:
            if 'childrens' not in bb:
                bb['childrens']=[]
            params = LookForParams(bb['childrens'],task) # look  by children
            if params is not None:
                break
    return params

def Count_Services(DAG,count=0,list_task=[]):
    for bb in DAG:
        count+=1
        list_task.append(bb['id'])
        count,list_task = Count_Services(bb['childrens'],count,list_task)
    return count,list_task

def validate_status_levels(actual_status,new_status):
    """
    status:: INFO > STARTING > RUNNING > OK > FINISHED 
                                       > ERROR > FAILED
    """
    def getstatus_level(st):
        status_level = 0
        if st == "INFO": 
            status_level =0
        if st == "STARTING": 
            status_level =1
        if st == "RUNNING": 
            status_level =2
        if st == "OK": 
            status_level =3
        if st == "ERROR": 
            status_level =3
        if st == "FINISHED": 
            status_level =4
        if st == "FAILED": 
            status_level =4
        return status_level

    level_actual = getstatus_level(actual_status)
    level_new = getstatus_level(new_status)

    if level_new > level_actual:
        return new_status
    else:
        return actual_status


def update_data(value): #called on bb report
    global BRANCHES
    RN = value['control_number']
    params = value['params']
    time_action = GetCurrentTimeAction()

    if "-MAP-" in params['task']: #is a map reduce result
        key_list = "subtask_list"
    elif "-subtask-" in params['task']: #is a subtask:
        key_list = "subtask_list"
    else: #normal task
        key_list = "task_list"

    if params['task'] not in BRANCHES[RN][key_list]: # if the task is new we create a new fingerprint

        BRANCHES[RN][key_list][params['task']]=dict()
        BRANCHES[RN][key_list][params['task']]['historic']=[]
        BRANCHES[RN][key_list][params['task']]['parent']=''
        BRANCHES[RN][key_list][params['task']]['status']='INFO'

        dag = LookForParams(BRANCHES[RN]["DAG"], params['task']) #look for the params of the task to create a fingerprint (if params are dfiferrent then the task is not the same)
        if dag is not None:  # if is not in the dag then is a subtask from the solution
            BRANCHES[RN][key_list][params['task']]['fingerprint']=Create_fingerprint(json.dumps(dag['params']))


    if 'dag' in params: #here are saved the dags from the subtask in order to recover in case of failure
        if "subdags" not in BRANCHES[RN]:
            BRANCHES[RN]["subdags"] = dict()
        BRANCHES[RN]["subdags"][params['task']] = params['dag']

    BRANCHES[RN][key_list][params['task']]['data_type'] = params['type']
    BRANCHES[RN][key_list][params['task']]['label'] = params['label']
    BRANCHES[RN][key_list][params['task']]['index'] = params['index']
    BRANCHES[RN][key_list][params['task']]['is_recovered']=False
    BRANCHES[RN][key_list][params['task']]['status'] = validate_status_levels(BRANCHES[RN][key_list][params['task']]['status'],params['status']) 
    BRANCHES[RN][key_list][params['task']]['message'] = params['message']
    BRANCHES[RN][key_list][params['task']]['historic'].append({'status':params['status'],'message':params['message'],'timestamp':time_action})
    BRANCHES[RN][key_list][params['task']]['last_update'] = time_action
    BRANCHES[RN][key_list][params['task']]['timestamp'] = time.time()

    if 'parent' in params:
        if params['parent'] != '':
            BRANCHES[RN][key_list][params['task']]['parent'] = params['parent']

def update_solution_status(token_solution,status):
    global BRANCHES
    BRANCHES[token_solution]["last_update"]=GetCurrentTimeAction()
    BRANCHES[token_solution]["status"] = status

def get_solution_status(token_solution):
    return {"status": BRANCHES[token_solution]["status"],"last_update":    BRANCHES[token_solution]["last_update"] }


def update_task_status_in_cascade(token_solution,childrens,status,message,parent=''):

    for child in childrens:
        params =json.dumps(child['params'])
        fp_dag = Create_fingerprint(params)
        id_service =child['id']
        if_exist=create_service_if_not_exist(token_solution,id_service,fp_dag,parent)
        if if_exist:
            update_task_status(token_solution,id_service,status,message,fingerprint=fp_dag,parent=parent)

        if 'childrens' in child:
            update_task_status_in_cascade(token_solution,child['childrens'],status,message,parent=id_service)

    return 0


def update_task_status(RN,task,status,message,details=None,is_recovered = False, fingerprint=None, parent =None ): #called on monitoring 
    global BRANCHES

    if "-MAP-" in task: #is a map reduce result
        key_list = "subtask_list"
    elif "-subtask-" in task: #is a subtask:
        key_list = "subtask_list"
    else: #normal task
        key_list = "task_list"


    time_action = GetCurrentTimeAction()
    BRANCHES[RN][key_list][task]['status']=status
    BRANCHES[RN][key_list][task]['message']=message
    BRANCHES[RN][key_list][task]['last_update']=time_action
    BRANCHES[RN]['last_update']=time_action #update solution status
    BRANCHES[RN][key_list][task]['timestamp']= time.time()

    if (is_recovered):
        BRANCHES[RN][key_list][task]['is_recovered'] = is_recovered

    if fingerprint is not None:
        BRANCHES[RN][key_list][task]['fingerprint']=fingerprint  # The fingerprint changed, so we save the new one
    if parent is not None:
        BRANCHES[RN][key_list][task]['parent']=parent  # The parent changed, so we save the new one
    if details is not None:
        BRANCHES[RN][key_list][task]['details']=details
    BRANCHES[RN][key_list][task]['historic'].append({'status':status,'message':message,'timestamp':time_action})

def Get_solution_if_exist(token_solution,auth):
    global BRANCHES
    solution = None
    SDB=Handler()
    if token_solution in BRANCHES:
        solution = BRANCHES[token_solution]
    elif SDB.Document_exist(auth['user'],token_solution):
        solution = SDB.Get_document(auth['user'],token_solution)
        BRANCHES[token_solution]=solution
        LOG.info("==============> recuperando datos de la BD")
    return solution

def GetSolutionData(token_project,token_solution): #this function will replace Get_solution_if_exist() in the future
    global BRANCHES
    solution = None
    SDB=Handler()
    if token_solution in BRANCHES:
        solution = BRANCHES[token_solution]
    elif SDB.Document_exist(token_project,token_solution):
        solution = SDB.Get_document(token_project,token_solution)
        BRANCHES[token_solution]=solution
        LOG.info("==============> recuperando datos de la BD")
    return solution

def create_service_if_not_exist(token_solution,id_service,fp_dag,parent):
    global BRANCHES
    if "-MAP-" in id_service: #is a map reduce result
        key_list = "subtask_list"
    elif "-subtask-" in id_service: #is a subtask:
        key_list = "subtask_list"
    else: #normal task
        key_list = "task_list"


    task_list =  BRANCHES[token_solution][key_list]
    if id_service in task_list:
        return True
    else:
        #must be registred in the task list 
        time_action = GetCurrentTimeAction()

        BRANCHES[token_solution][key_list][id_service]=dict()
        BRANCHES[token_solution][key_list][id_service]['historic']=[]
        BRANCHES[token_solution][key_list][id_service]['parent']=parent
        BRANCHES[token_solution][key_list][id_service]['fingerprint']=fp_dag
        BRANCHES[token_solution][key_list][id_service]['is_recovered']=False
        BRANCHES[token_solution][key_list][id_service]['data_type'] = ''
        BRANCHES[token_solution][key_list][id_service]['label'] = ''
        BRANCHES[token_solution][key_list][id_service]['index'] = ''
        BRANCHES[token_solution][key_list][id_service]['status'] = 'STARTING'
        BRANCHES[token_solution][key_list][id_service]['message'] = 'NEW SERVICE ADDED.. STARTING EXECUTION.'
        BRANCHES[token_solution][key_list][id_service]['last_update'] = time_action
        BRANCHES[token_solution][key_list][id_service]['timestamp'] = time.time()
        return False


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
        if_exist=create_service_if_not_exist(token_solution,id_service,fp_dag,parent)

        if if_exist:

            taskInSolution = solution['task_list'][id_service]
            Fingerprints_comparation = Compare_fingerprints(taskInSolution['fingerprint'],fp_dag)
            parent_comparation = Compare_parents(taskInSolution['parent'],parent) 

            LOG.debug("LA COMPARACION DE FP ES %s para la tarea %s con status %s" %(Fingerprints_comparation,id_service,taskInSolution['status']))
            LOG.debug("LA COMPARACION DE PADRES ES %s para la tarea %s con status %s" %(parent_comparation,id_service,taskInSolution['status']))


            if (Fingerprints_comparation and taskInSolution['status']=="FINISHED" and parent_comparation):
                #validate status and fingerprints
                update_task_status(token_solution,id_service,"OK","Task has no changes",is_recovered = True)
                
                children_dag = validate_solution(childrens,solution,token_solution,parent=id_service)
                for x in children_dag:
                    new_dag.append(x)
            
            elif taskInSolution['status']=="STARTING":
                pass
            else:    
                new_dag.append(taskInDag)
                update_task_status(token_solution,id_service,"STARTING","Task has changes",fingerprint=fp_dag,parent=parent)
                update_task_status_in_cascade(token_solution,childrens,"STARTING","Parent task has changes",parent=id_service)

        else: #it is new
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

        LOG.info("====== STATUS DE LA SOLUCION ======")
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
        BRANCHES[RN]["subtask_list"]=dict()
        BRANCHES[RN]["subdags"]=dict()

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
    query = {} 
    if 'params' in value:
        query = value['params']
    SDB = Handler() 
    list_solutions_of_user = SDB.List_document(auth['user'],query)
    return list_solutions_of_user




def get_task_runtime_info(value): #new version of consult data
    RN = str(value['control_number'])
    token_project = str(value['token_project'])

    kind = "task_list"
    if 'kind_task' in value:
        kind = value['kind_task']

    list_info={}

    solution =GetSolutionData(token_project,RN) # solution has a copy of the info in the current timestamp. 
    solution_dag = solution['DAG']
    while(True):
        try:
            solution_task_list = copy.copy(solution[kind])
            break
        except Exception as e:
            #fallo porque cambio, hay que volver a intentar hasta que se pueda
            pass
    
    n_task,list_original_task = Count_Services(solution['DAG'])
    
    count_error_task=0
    count_finished_task = 0

    count_error_subtask=0
    count_finished_subtask = 0

    if 'monitoring_tasks' in value:
        tmp={}
        for tsk in value['monitoring_tasks']: #[]
            if tsk in solution_task_list:
                tmp[tsk] = solution_task_list[tsk]

        solution_task_list = tmp

        #LOG.info("numero de tareas a monitorear: %s" % len(solution_task_list))

    for task,val in solution_task_list.items():
        ToSend = {'status':"WAITING"}
        st =  val['status']
        data_type = val['data_type']
        idx_opt = val['index']
        is_recovered = val['is_recovered']

        if (val['status']=="RUNNING" or val['status']=="INFO") and time.time()-val['timestamp'] > 60: #if has passed more than 60 seg of the last health check of one service
            update_task_status(RN,task,"CRITICAL","Resource %s is not responding. last message: %s." % (task, val['message']),details="RESOURCE DOWN")
            #temp_dag = LookForParams(solution_dag,task) #si esto es none entonces no esta en el dag original
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            ToSend['DAG'] = solution["subdags"][task]

            ToSend['parent'] =  val['parent'] 
            LOG.info("================================== SE VA A RECUPERAR: %s" % task)
            #LOG.info("el dag es : %s" % val['dag'])

        elif val['status'] == "FINISHED" or val['status'] == "FAILED":
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            if val['status'] == "FINISHED":
                if task in list_original_task:
                    count_finished_task+=1
                else:
                    count_finished_subtask+=1

            if val['status'] == "FAILED":
                if task in list_original_task:
                    count_error_task+=1
                else:
                    count_error_subtask+=1                # since it failed, we need to update all his childrens


        elif val['status'] == "OK":
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            #if kind=="subtask_list":
            #    del solution["subdags"][task]
            update_task_status(RN,task,"FINISHED","Execution completed without errors")

        elif val['status']=="ERROR":
            ToSend = {"status":st,"task":task,"type":data_type,"message":val['message'],"index":idx_opt,"is_recovered":is_recovered }
            update_task_status(RN,task,"FAILED",val['message'])
            
            #tree_task = LookForParams(solution_dag,task) 
            #if tree_task is None:
            #    tree_task = solution["subdags"][task] #is a subtask
            tree_task = solution["subdags"][task] #is a subtask

            update_task_status_in_cascade(RN,tree_task['childrens'],"FAILED","Parent task have failed",parent=task)
            #if kind=="subtask_list":
            #    del solution["subdags"][task]

        else:
            pass
            #LOG.info("=======> sigo espetando: %s" % task)

        if 'show_history' in value:
            ToSend['historic']=val['historic']

        list_info[task]=ToSend

    if 'monitoring_tasks' not in value:
        LOG.info("numero de tareas: %s" % n_task)
        LOG.info("numero de tareas terminadas: %s" % count_finished_task)
        LOG.info("numero de subtareas terminadas: %s" % count_finished_subtask)
        if 'subtask_list' in solution:
            LOG.info("numero de subtareas: %s" % len(solution["subtask_list"]))
        LOG.info("numero de tareas fallidas: %s" % count_error_task)
        LOG.info("numero de subtareas fallidas: %s" % count_error_subtask)

    if count_finished_task+count_error_task==n_task:
        if count_error_task>0:
            update_solution_status(RN,"FAILED")
        else:
            update_solution_status(RN,"FINISHED")



    return list_info


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


    ## READ ACTIONS
    if action=="STATUS":#add workload
        return LOAD_B.GetStatus()
    elif action=="SELECT":#select a resource
        return LOAD_B.decide(service, action_params['context']) #search services in the same context


    context = data_bin['context']
    resource_in_context_id = service_id+"-"+context

    if action=="ADD":
        status = LOAD_B.Addresource(service,resource_in_context_id,data_bin)
        if status:
            LOG.debug("REGISTRED %s, ip:%s" % (service,resource_in_context_id))
        else:
            LOG.debug("ALREADY REGISTRED %s, ip:%s" % (service,resource_in_context_id))
        res = {'status':'OK'}
    elif action=="DISABLE":#when a node is down
        LOAD_B.NodeDown(service,resource_in_context_id)
        res = {'status':'OK'}
    elif action=="ADD_WORKLOAD":#add workload
        LOAD_B.AddWorkload(service,resource_in_context_id,n=1)
        res = {'status':'OK'}

    return res


def ManageProductMap(action,value):
    """
    value {
        action::create,get, AddProduct
        action_params{service,service_id,context}
        data_bin: {}
    }
    """
    pass



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
    #LOG.info(action)


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
        task_info  = get_task_runtime_info(value)
        solution_info = get_solution_status(str(value['control_number']))
        res = {"tasks":task_info,"solution":solution_info}
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "CONSULT_V2":
        value = params['value']
        task_info  = get_task_runtime_info(value)
        solution_info = get_solution_status(str(value['control_number']))
        res = {"tasks":task_info,"solution":solution_info}
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "RESOURCES":
        value = params['value']
        res = ResourcesManagment(value['action'],value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    elif action == "PRODUCTS_MAP":
        value = params['value']
        res = ManageProductMap(value['action'],value)
        return json.dumps({"status":"OK","action":"ACCEPT","value":res})

    else:
        return {"status":"ERROR","value":"Something happend"}



if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=80,debug = True)
    serve(app, host='0.0.0.0', port=80)
