import sys,os,pandas,ast
from threading import Thread
from flask import request, url_for
from flask import Flask, request,jsonify,Response
from random import randint
import json
from time import sleep
import C
from TPS.Builder import Builder #TPS API BUILDER
import logging #logger

########## GLOBAL VARIABLES ###########
LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMERSH"
TPSHOST ="http://tps_manager:5000"

INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data

with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services

#select distribution algorithm
if(dictionary['config']['Distribution_Type'] == "Round Robin"):
    from T_i import roundRobin as coordinate
elif(dictionary['config']['Distribution_Type'] == "Pseudorandom"):
    from T_i import pseudorandom as coordinate
elif(dictionary['config']['Distribution_Type'] == "Two Choice"):
    from T_i import twoChoice as coordinate

BRANCHES = dict() #dict of all the REQUEST

###### END GLOBAL VARIABLES ##########

def IndexData(RN,id_service,data):
    #data must be a json (dict)
    global INDEXER

    data_label = "%s_%s" % (RN,id_service) #this is the name of the document (mongo document)
    query = INDEXER.TPSapi.format_single_query("notImportant") #not important line. Well yes but actually no.
    res = INDEXER.TPSapi.TPS(query,"getdata",workload=data,label=data_label) #this service (getdata) let me send json data and save it into a mongo DB
    LOGER.warning(res)
    return data_label

def GetIndexedData(label):
    #data must be a json (dict)
    global INDEXER
    query = INDEXER.TPSapi.format_single_query(label)
    data = INDEXER.TPSapi.TPS(query,"getdata") #this service (getdata) let me send json data and save it into a mongo DB
    return data
    
def readActions(actionsString):
    actions = actionsString.split(",")
    return actions

def formPMsg(data,p_DAG,destinationFolder,destinationFile,workParams):
    msg = data,destinationFolder,destinationFile,p_DAG,workParams
    return msg

def formDLMsg(data,dl_DAG,destinationFolder,destinationFile,filename,workParams):
    msg = data,destinationFolder,destinationFile,dl_DAG,filename,workParams
    return msg

def EXE_SERVICE(control_number,data,info):
    global BRANCHES
    service = info['service']
    params = info['params']
    id_service =info['id']
    ToSend = {'data':json.dumps(data),'params':params} #no actions, so it will taken the default application A
    if 'actions' in info: ToSend['actions']= info['actions']
    
    LOGER.error(type(data))
    data_result = json.loads(execute_service(service,ToSend)) #send request to service
    LOGER.error(type(data_result))
    label = IndexData(control_number,id_service,data_result) #indexing result data into DB

    
    BRANCHES[control_number][id_service]={'status':"FINISHED","label":label,"task":id_service} #update status

    #the task fihised, and now we execute the children task
    DAG = info['childrens']
    for br in DAG: #for each service in DAG
        thread1 = Thread(target = EXE_SERVICE, args = (control_number,data_result,br,) )
        thread1.start()


app = Flask(__name__)
#root service
@app.route('/')
def prueba():
    return "Service Mersh"

#service to execute applications
@app.route('/execute/<service>', methods=['POST'])
def execute_service(service,params=None):
    if params is None:
        params = request.get_json()
    data = params['data'] #data to be transform
    service_params = params['params'] #parameters for the service
    if 'actions' in params:
        actions=params['actions'] #for the geoportal we just gona use a single set of actions
    else:
        actions = ['A'] #default exec the first service called A
        service_params = {'A':service_params}
    
    info_service = dictionary['services'][service] #get all the configurations from an specific service

    coordinator = coordinate(len(info_service['resources']),actions) #select the resource
    
    list_resources = info_service['resources'] #list of dictionaries

    for package in coordinator:
        p_DAG = actions[package] #dag of applications
        res = list_resources[coordinator[package]]
        ip = res['ip']
        port = res['port']

        #send message to BB
        # folder is always ./ so its not necessary to add as a parameter
        msg = {
            'data':data,
            'actions':p_DAG,
            'params':service_params
            }

        data = C.RestRequest(ip,port,msg)
    return data


#service to execute a set of application in a DAG
@app.route('/executeDAG', methods=['POST'])
def execute_DAG():
    global BRANCHES
    params = request.get_json()
    data = json.loads(params['data']) #data to be transform
    DAG = params['DAG'] #it have the parameters, the sub dag ,and the secuence of execution (its a json).
    #a Resquest No is created. This request number it to monitorin the execution.
    RN = str(randint(100000,900000)) #random number with 6 digits

    #execute dag
    BRANCHES[RN]=dict()
    for br in DAG: #for each service in DAG
        thread1 = Thread(target = EXE_SERVICE, args = (RN,data,br,) )
        thread1.start()

    return json.dumps({'RN':RN})


#service to monitoring a solution with a control number
@app.route('/monitor/<RN>', methods=['POST'])
def monitoring_solution(RN):
    #list of task
    global BRANCHES
    task_dict = BRANCHES[str(RN)]
    sleep(1)
    for key,value in task_dict.items():
        if value['status'] == "FINISHED":
            BRANCHES[RN][key]['status']="STANDBY" #status stamdby is for a task which already finished and it has been accounted
            label = value['label']
            task = value['task']
            data = GetIndexedData(label) #get data from label
            return json.dumps({'status':"OK",'data':data,"task":task})
    return json.dumps({'status':"ERROR"}) #no task found


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555,debug = True)
