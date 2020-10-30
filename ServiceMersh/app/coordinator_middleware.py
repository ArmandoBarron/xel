import sys,os,pandas,ast
from threading import Thread
from flask import request, url_for
from flask import Flask, request,jsonify,Response,send_file
from random import randint
import json
from time import sleep
import C
from TPS.Builder import Builder #TPS API BUILDER
import logging #logger
from base64 import b64encode,b64decode
import io
import time

########## GLOBAL VARIABLES ###########
LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMERSH"
TPSHOST ="http://tps_manager:5000"

#create logs folder
logs_folder= "./logs/"
try:
    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder)
except FileExistsError:
    pass

#fh = logging.FileHandler(logs_folder+'info.log')
#fh.setLevel(logging.error)

         


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
FINISHED_BRANCH = dict()
###### END GLOBAL VARIABLES ##########

def IndexData(RN,id_service,data):
    #data must be a json (dict)
    global INDEXER
    try:
        INDEXER.TPSapi.format_single_query("notImportant")
    except AttributeError:
        global WORKSPACENAME, TPSHOST
        INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data


    data_label = "%s_%s" % (RN,id_service) #this is the name of the document (mongo document)
    query = INDEXER.TPSapi.format_single_query("notImportant") #not important line. Well yes but actually no.
    res = INDEXER.TPSapi.TPS(query,"indexdata",workload=data,label=data_label) #this service (getdata) let me send json data and save it into a mongo DB
    return data_label

def GetIndexedData(label):
    #data must be a json (dict)
    global INDEXER
    try:
        INDEXER.TPSapi.format_single_query("notImportant")
    except AttributeError:
        global WORKSPACENAME, TPSHOST
        INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data

    data = INDEXER.TPSapi.GetData(label)['DATA']
    #data = INDEXER.TPSapi.TPS(query,"getdata") #this service (getdata) let me send json data and save it into a mongo DB
    #LOGER.error(data)
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
    if 'SAVE_DATA' in params:        
        index_opt = params['SAVE_DATA']
    else:
        for key in params:
            if 'SAVE_DATA' in params[key]:
                index_opt = params[key]['SAVE_DATA']
                break
            else:
                index_opt = False
                
    id_service =info['id']
    ToSend = {'data':data,'params':params} #no actions, so it will taken the default application A
    del data
    if 'actions' in info: ToSend['actions']= info['actions']

    BB_ST = time.time(); f = open(logs_folder+'log_'+control_number+'.txt', 'a+');  #<--- time flag
    data_result = execute_service(service,ToSend) #send request to service {data:,type:}
    f.write("%s, %s \n" %(service,(time.time() - BB_ST))); f.close() #<--- time flag
    LOGER.error(data_result['status'])

    del ToSend
    
    if index_opt: 
        IX_ST = time.time() #<--- time flag
        f = open(logs_folder+'log_'+control_number+'.txt', 'a+') # times log
        label = IndexData(control_number,id_service,data_result) #indexing result data into DB
        f.write("index_%s, %s \n" %(service,(time.time() - IX_ST))) #<--- time flag
        f.close()
    else:
        label=False
        LOGER.info("skiping index process")

    
    BRANCHES[control_number][id_service]={'status':data_result['status'],"message":data_result["message"],"label":label,"task":id_service,"type":data_result['type'], "index":index_opt} #update status

    #the task fihised, and now we execute the children task
    try:
        DAG = info['childrens']
        for br in DAG: #for each service in DAG
            thread1 = Thread(target = EXE_SERVICE, args = (control_number,data_result,br,) )
            thread1.start()
    except KeyError as ke:
        LOGER.error("No more childrens")


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
        actions=[params['actions']] #for the geoportal we just gona use a single set of actions
    else:
        actions = ['A'] #default exec the first service called A
        service_params = {'A':service_params}
    
    info_service = dictionary['services'][service] #get all the configurations from an specific service

    coordinator = coordinate(len(info_service['resources']),actions) #select the resource
    
    list_resources = info_service['resources'] #list of dictionaries

    LOGER.error("executing...%s"% service)
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

    LOGER.error("finishing execution...%s"% service)

    return data

#service to execute a set of application in a DAG
@app.route('/executeDAG', methods=['POST'])
def execute_DAG():
    global BRANCHES
    global FINISHED_BRANCH
    params = request.get_json(force=True)
    data = json.loads(params['data']) #data to be transform {data:,type:}
    #LOGER.error("----------- type:"+data['type'])

    #

    DAG = json.loads(params['DAG']) #it have the parameters, the sub dag ,and the secuence of execution (its a json).
    #a Resquest No is created. This request number it to monitorin the execution.
    RN = str(randint(100000,900000)) #random number with 6 digits

    #verify if data its a csv or a binary

    #execute dag
    BRANCHES[RN]=dict()
    FINISHED_BRANCH[RN]=dict()

    for br in DAG: #for each service in DAG
        thread1 = Thread(target = EXE_SERVICE, args = (RN,data,br,) )
        thread1.start()

    return json.dumps({'RN':RN})


#service to monitoring a solution with a control number
@app.route('/monitor/<RN>', methods=['POST'])
def monitoring_solution(RN):
    #list of task
    global BRANCHES
    global FINISHED_BRANCH
    task_dict = BRANCHES[str(RN)]
    sleep(1)
    for key,value in task_dict.items():
        if value['status'] == "OK" or value['status']=="ERROR":
            st =  value['status']
            BRANCHES[RN][key]['status']="STANDBY" #status stamdby is for a task which already finished and it has been count
            label = value['label']
            task = value['task']
            data_type = value['type']
            idx_opt = value['index']
            FINISHED_BRANCH[RN][task]=label #to get data in future
            return json.dumps({"status":st,"task":task,"type":data_type,"message":value['message'],"index":idx_opt })
    return json.dumps({'status':"WAITING"}) #no task found


@app.route('/getdata/<RN>/<task>', methods=['POST'])
def getdataintask(RN,task):
    #list of task
    global FINISHED_BRANCH
    label = FINISHED_BRANCH[RN][task]
    data = GetIndexedData(label) #get data from label
    return json.dumps({'status':"OK","data":data}) #no task found

@app.route('/getfile/<RN>/<task>', methods=['GET'])
def getfileintask(RN,task):
    #list of task
    global FINISHED_BRANCH
    label = FINISHED_BRANCH[RN][task]
    data = GetIndexedData(label) #get data from label
    data_ext = data['type']
    data = b64decode(data['data'].encode())


    return send_file(
                io.BytesIO(data),
                as_attachment=True,
                attachment_filename=task+'.'+data_ext
        )

@app.route('/getlog/<RN>', methods=['GET'])
def getLogFile(RN):
    return send_file(logs_folder+'log_'+RN+'.txt',as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555,debug = True)
