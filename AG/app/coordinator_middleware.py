import sys,os,ast
import pandas as pd
from threading import Thread
from flask import request, url_for
from flask import Flask,jsonify,Response,send_file
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
import tempfile

def createFolderIfNotExist(folder_name,wd=""):
    try:
        if not os.path.exists(wd+folder_name):
            os.makedirs(wd+folder_name)
    except FileExistsError:
        pass
    return wd+folder_name

########## GLOBAL VARIABLES ##########
with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services

LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMESH"
TPSHOST ="http://tps_manager:5000"
NETWORK=os.getenv("NETWORK") 

#create logs folder
logs_folder= "./logs/"
createFolderIfNotExist(logs_folder)

BKP_FOLDER= "./BACKUPS/"
createFolderIfNotExist(BKP_FOLDER)

#fh = logging.FileHandler(logs_folder+'info.log')
#fh.setLevel(logging.error)

INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data

#select load blaancer
LOAD_B = loadbalancer(dictionary)
Tolerant_errors=25 #total of errors that can be tolarated
ACCEPTORS_LIST= dictionary['paxos']["accepters"]
PROPOSER = Paxos(ACCEPTORS_LIST)
########## END GLOBAL VARIABLES ##########

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
    return data
    

def formPMsg(data,p_DAG,destinationFolder,destinationFile,workParams):
    msg = data,destinationFolder,destinationFile,p_DAG,workParams
    return msg

def formDLMsg(data,dl_DAG,destinationFolder,destinationFile,filename,workParams):
    msg = data,destinationFolder,destinationFile,dl_DAG,filename,workParams
    return msg

#service to execute applications
def execute_service(service,metadata):
    f = open(metadata['data']['data'],"rb")

    LOGER.error("executing...%s"% service)
    errors_counter=0
    ToSend = {'service':service,'network':NETWORK} #update status of falied node
    res = json.loads(ASK(params=ToSend))

    while(True): # AVOID ERRORS
        if res is None: #no more resources avaiable
            data= {'data':'','type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
            WARN(params={'status':data['status'],"message":data["message"],"label":"FALSE","task":metadata['DAG']['id_service'],"type":data['type'], "index":False}) #update status
            break
    
        try:
            ip = res['ip']
            port = res['port']
        except KeyError as ke:
            data= {'data':'','type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
            WARN(params={'status':data['status'],"message":data["message"],"label":"FALSE","task":metadata['DAG']['id_service'],"type":data['type'], "index":False}) #update status
            break


        #send message to BB
        data = C.RestRequest(ip,port,metadata,data_file=f)

        if data is not None:
            LOGER.error(">>>>>>> SENT WITH NO ERRORS")
            errors_counter=0
            break
        else:
            errors_counter+=1
            LOGER.error(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
            if errors_counter>Tolerant_errors: #we reach the limit
                    ######## ASK AGAIN #######
                    ToSend = {'service':service,'network':NETWORK,'update':{'id':res['id'],'status':'DOWN','type':res['type']}} #update status of falied node
                    res = json.loads(ASK(params=ToSend))
                    errors_counter=0 #reset counter 
                    #------------------#
                    if 'info' in res: #no more nodes
                        res = None
                    else:
                        ip = res['ip'];port = res['port']
                        LOGER.error("TRYING A NEW NODE... IP:%s PORT: %s " %(ip,port) )
    LOGER.error("finishing execution...%s"% service)


app = Flask(__name__)
#root service
@app.route('/')
def prueba():
    return "Service Mesh"

@app.route('/health',methods=['GET'])
def health():
    return json.dumps({"status":"OK"})

@app.route('/SAVE_CONFIG', methods=['GET'])
def saveconfig():
    LOAD_B.Save_config_file()
    return json.dumps({'status':'OK'})

@app.route('/ADD', methods=['POST'])
def AddServiceResource():

    params = request.get_json(force=True)

    service = params['SERVICE']
    service_ip = params['IP']
    service_port = params['PORT']
    network = params['NETWORK']
    
    ToSend={"network":network,"ip":service_ip,"port":service_port,"status":"UP"}
    status = LOAD_B.Addresource(service,ToSend)
    if status:
        LOGER.error("REGISTRED %s, ip:%s port: %s" % (service,service_ip,service_port))
    else:
        LOGER.error("ALREADY REGISTRED %s, ip:%s port: %s " % (service,service_ip,service_port))

    return json.dumps({'status':'OK'})



@app.route('/ASK', methods=['POST'])
def ASK(params=None):
    if params is None:
        params = request.get_json(force=True)

    service = params['service'] #service name
    network = params['network']
    n=1 #quantity of workload added to resource
    force = None
    if 'force' in params: #option for gateways, gateways are forced to select a resource in the same network
        force = True
        n = 0

    if 'update' in params: #update node status
        info = params['update'] #{id,status,type}
        if info['status'] == "DOWN":
            if info['type']=="service":
                LOAD_B.NodeDown(service,info['id'])
            elif info['type']=="gateway":
                LOAD_B.GatewayDown(info['id'])
            else:
                LOGER.error("ERROR in update. type")
                
    while(True):
        res= LOAD_B.decide(service,network,force_network=force,n=n) #search services in the same network
        if res is None: #no more avaiable resources
            return json.dumps({'info':'ERROR'})

        res['type'] = "service" #add type
        if res['network'] != network: #redirect to gateway
            LOGER.error("REDIRECTING TO INTERNAL GATEWAY..")
            #

            iag = LOAD_B.SelectGateway(res['network'])
            if iag is not None:
                res = iag
                res['type'] = "gateway"
                LOGER.error("GATEWAY: %s, NETWORK: %s" %(res['ip'],res['network']))
                break
            else:
                LOGER.error("Gateway is not aviable")
                LOAD_B.NetworkDown(service,res['network'])  #update set all service of the network
        else: #service is in the same network
            LOAD_B.AddWorkload(service,res['id'])
            break

    return json.dumps(res)


@app.route('/STATUS', methods=['GET'])
def services_status():
    services = LOAD_B.GetStatus()
    return jsonify(services)


@app.route('/TIMES', methods=['POST'])
def TIMES():
    params = request.get_json(force=True)
    tmp= params['times']
    control_number = params['control_number']

    f = open(logs_folder+'log_'+control_number+'.txt', 'a+'); 
    f.write("%s, %s, %s, %s \n" %(tmp['NAME'],tmp['ACQ'],tmp['EXE'],0,)) 
    f.close()
    return json.dumps({'status':'OK'})


@app.route('/WARN', methods=['POST'])
def WARN(params=None):
    if params is None:
        params = request.get_json(force=True)

    status = params['status']
    message = params['message']
    label = params['label']
    id_serv = params['id']
    data_type = params['type']
    index_opt = params['index']
    control_number = params['control_number']

    ToSend={'status':status,"message":message,"label":label,"task":id_serv,"type":data_type, "index":index_opt} #update status

    if 'parent' in params:
        ToSend['parent'] = params['parent']

    ######## paxos ##########
    paxos_response = PROPOSER.Update_task(control_number,ToSend) # save request in paxos distributed memory
    if paxos_response['status'] == "ERROR":
        LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
    #########################

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

    params = request.get_json(force=True)
    data = json.loads(params['data']) #data to be transform {data:,type:}

    DAG = json.loads(params['DAG']) #it have the parameters, the sub dag ,and the secuence of execution (its a json).
    #A resquest random number for monitoring is created. 
    RN = str(randint(100000,900000)) #random number with 6 digits

    INPUT_TEMPFILE = tempfile.NamedTemporaryFile(delete=False,suffix="."+data['type']) #create temporary file
    input_temp_filename = INPUT_TEMPFILE.name
    INPUT_TEMPFILE.close()

    if data['data']=="": #if nothing was sent
        data['data']="WAKE ME UP INSIDE.."
        data['type']="txt"

    if data["type"]=="csv": # to parse json to csv
        input_data = pd.DataFrame.from_records(data['data']) #data is now a dataframe
        input_data.to_csv(input_temp_filename, index = False, header=True) #write DF to disk
    else:
        f = open(input_temp_filename,"wb")
        f.write(data['data'].encode())
        f.close()

    data['data']=input_temp_filename

    ######## paxos ##########
    paxos_response = PROPOSER.Save(RN,DAG) # save request in paxos distributed memory
    if paxos_response['status'] == "ERROR":
        LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
        return {"status":"ERROR","message":"Mesh is not accepting requests"}
    #########################

    for br in DAG: #for each pipe in DAG
        br['control_number'] = RN
        metadata = {"data":data,"DAG":br}
        service = br['service']

        thread1 = Thread(target = execute_service, args = (service,metadata) )
        thread1.start()
        time.sleep(1)

    return json.dumps({"status":"OK",'RN':RN})


#service to monitoring a solution with a control number
@app.route('/monitor/<RN>', methods=['POST'])
def monitoring_solution(RN):
    #list of task
    sleep(1)
    ######## paxos ##########
    paxos_response = PROPOSER.Consult(RN) # consult request in paxos distributed memory
    #########################
    value = paxos_response['value']

    if 'DAG' in value:
        #el nodo fallo al estar procesando datos... se van a recuperar
        params = value['DAG']
        path_bk_data = "%s%s/%s" %(BKP_FOLDER,RN,params['parent'])
        tmp = os.listdir(path_bk_data)
        path_bk_data +="/"+tmp[0]
        #LOGER.error("recuperando datos de %s ..." % path_bk_data)

        params['DAG']['control_number'] = RN
        data ={"data":path_bk_data,"type":path_bk_data.split(".")[-1]}
        metadata = {"data":data,"DAG":params['DAG']}
        service = params['DAG']['service']

        thread1 = Thread(target = execute_service, args = (service,metadata))
        thread1.start()
        return json.dumps({"status":"INFO", "message":"RECOVERING DATA FROM %s" % service})


    if value is None:
        return json.dumps({"status":"ERROR", "message":"PAXOS ERROR"})
    else:
        return json.dumps(value) 


@app.route('/getdata/<RN>/<task>', methods=['POST'])
def getdataintask(RN,task):
    ######## paxos ##########
    paxos_response = PROPOSER.Consult(RN,params={"task":task}) # consult request in paxos distributed memory
    #########################

    value = paxos_response['value']
    if value is None:
        return json.dumps({"status":"ERROR", "message":"PAXOS ERROR"})
    else:
        label = value['label']
        data = GetIndexedData(label) #get data from label
        if data['type'] == "csv":
            newFile = open("tempfile.csv", "wb")
            newFile.write(b64decode(data['data'].encode()))
            newFile.close()

        tempdf = pd.read_csv("tempfile.csv")
        data['data'] = json.loads(tempdf.to_json(orient="records"))
        return json.dumps({'status':"OK","data":data}) #no task found

@app.route('/getfile/<RN>/<task>', methods=['GET'])
def getfileintask(RN,task):
    ######## paxos ##########
    paxos_response = PROPOSER.Consult(RN,params={"task":task}) # consult request in paxos distributed memory
    #########################
    value = paxos_response['value']
    if value is None:
        return json.dumps({"status":"ERROR", "message":"PAXOS ERROR"})
    else:
        label = value['label']

        data = GetIndexedData(label) #get data from label
        data_ext = data['type']
        data = b64decode(data['data'].encode())

        return send_file(
                    io.BytesIO(data),
                    as_attachment=True,
                    attachment_filename=task+'.'+data_ext
            )



@app.route('/ArchiveData/<RN>/<id_service>', methods = ['POST'])
def upload_file(RN,id_service):
    tmp_f = createFolderIfNotExist("%s/" % RN,wd=BKP_FOLDER)
    path_to_archive= createFolderIfNotExist("%s/" % id_service,wd=tmp_f)
    f = request.files['file']
    filename = f.filename
    f.save(os.path.join(path_to_archive, filename))
    return json.dumps({"status":"OK", "message":"OK"})


@app.route('/DescribeDataset', methods=['POST'])
def describeDataset():
    data = request.get_json()
    datos= data['data']
    datos = pd.DataFrame.from_records(datos)
    columns = ['count','unique','top','freq','mean','std' ,'min' ,'q_25' ,'q_50' ,'q_75' ,'max']

    datos = datos.apply(pd.to_numeric, errors='ignore')
    
    response = dict()
    response['info']=dict()
    response['columns'] = list(datos.columns.values)
    des = datos.describe(include='all')
    for col in response['columns']:
        des_col = des[col]
        column_description = dict()
        for c in range(0,len(columns)):
            try:
                value = des_col[c]
            except Exception:
                break
            if pd.isnull(value) or pd.isna(value):
                value = ""
            column_description[columns[c]] = str(value)
        column_description['type'] = datos[col].dtype.name
        response['info'][col] = column_description
        LOGER.error(column_description)
    return json.dumps(response)


@app.route('/getlog/<RN>', methods=['GET'])
def getLogFile(RN):
    return send_file(logs_folder+'log_'+RN+'.txt',as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555,debug = True)
