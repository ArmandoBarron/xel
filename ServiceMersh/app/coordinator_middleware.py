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
from TwoChoices import loadbalancer
from Proposer import Paxos


########## GLOBAL VARIABLES ###########
LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMESH"
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

#select load blaancer
LOAD_B = loadbalancer(dictionary['services'])
Tolerant_errors=25 #total of errors that can be tolarated


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

def Execute_pipe(control_number,data,info):
    global BRANCHES
    service = info['service']
    service_name = service
    params = info['params']
    DAG = info['childrens']
    id_service =info['id']
    info['control_number'] = control_number


    ToSend = {'data':data,'DAG':info} #no actions, so it will taken the default application A
    del data

    execute_service(service,ToSend) #send request to service {data:,type:}

    del ToSend

#service to execute applications
def execute_service(service,msg):
    global BRANCHES

    ######## paxos ##########
    acc = dictionary['paxos']["accepters"]
    proposer = Paxos(acc)
    proposer.process()
    #########################

    LOGER.error("executing...%s"% service)
    errors_counter=0

    while(True): # AVOID ERRORS
        res= LOAD_B.decide(service)

        ip = res['ip']
        port = res['port']
        LOGER.error(res['workload'])

        #send message to BB
        # folder is always ./ so its not necessary to add as a parameter
 
        data = C.RestRequest(ip,port,msg)

        if data is not None:
            LOGER.error(">>>>>>> SENT WITH NO ERRORS")
            errors_counter=0
            break;
        else:
            errors_counter+=1
            LOGER.error(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
            if errors_counter>Tolerant_errors: #we reach the limit
                data= {'data':'','type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
                BRANCHES[msg['DAG']['control_number']][msg['DAG']['id']]={'status':data['status'],"message":data["message"],"label":"FALSE","task":msg['DAG']['id_service'],"type":data['type'], "index":False} #update status
                break

    LOGER.error("finishing execution...%s"% service)




app = Flask(__name__)
#root service
@app.route('/')
def prueba():
    return "Service Mersh"


@app.route('/ASK', methods=['POST'])
def ASK():
    params = request.get_json(force=True)
    service = params['service'] #service name
    
    ######## paxos ##########
    acc = dictionary['paxos']["accepters"]
    proposer = Paxos(acc)
    proposer.process()
    #########################
    LOGER.error("executing...%s"% service)
    errors_counter=0

    res= LOAD_B.decide(service)

    LOGER.error(res['workload'])
 
    return json.dumps(res)




@app.route('/WARN', methods=['POST'])
def WARN():
    global BRANCHES
    params = request.get_json(force=True)
    status = params['status']
    message = params['message']
    label = params['label']
    id = params['id']
    data_type = params['type']
    index_opt = params['index']
    control_number = params['control_number']

    BRANCHES[control_number][id]={'status':status,"message":message,"label":label,"task":id,"type":data_type, "index":index_opt} #update status

    if 'times' in params:
        tmp= params['times']
        f = open(logs_folder+'log_'+control_number+'.txt', 'a+'); 
        #{"NAME":service_name,"ACQ":data_acq_time,"EXE":execution_time,"IDX":index_time}
        f.write("%s, %s, %s, %s \n" %(tmp['NAME'],tmp['ACQ'],tmp['EXE'],tmp['IDX'], )) 
        f.close()
    return json.dumps({'status':'OK'})


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

    for br in DAG: #for each pipe in DAG
        thread1 = Thread(target = Execute_pipe, args = (RN,data,br,) )
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
