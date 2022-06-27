from cgitb import reset
import sys,os,ast
import pandas as pd
from threading import Thread
from flask import Flask,request,jsonify,send_file
#from waitress import serve

import json
from time import sleep
import C
import logging #logger
from base64 import b64encode,b64decode
import io
import tempfile
import shutil
import time

# local imports
from functions import *
from Proposer import Paxos
from os import listdir
import chardet


########## GLOBAL VARIABLES ##########
dictionary = dict()
with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services

logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMESH" #equivalente a catalogo en skycds, es decir, una solucion o un DAG
#TPSHOST ="http://tps_manager:5000"
NETWORK=os.getenv("NETWORK") 

#create logs folder
logs_folder= "./logs/"
createFolderIfNotExist(logs_folder)
#fh = logging.FileHandler(logs_folder+'info.log')

#Backups folder
BKP_FOLDER= "./BACKUPS/"
createFolderIfNotExist(BKP_FOLDER)

#supplies folder
SPL_FOLDER= "./SUPPLIES/"
createFolderIfNotExist(SPL_FOLDER)

#select load blaancer
Tolerant_errors=25 #total of errors that can be tolarated
ACCEPTORS_LIST= dictionary['paxos']["accepters"]
LOGER.info(ACCEPTORS_LIST)
PROPOSER = Paxos(ACCEPTORS_LIST)
########## END GLOBAL VARIABLES ##########

def GetDataPath(params):
    typeOfData = params['type']
    credentials = params['data']
    if typeOfData=="RECORDS":
        input_data = pd.DataFrame.from_records(data['data']) #data is now a dataframe
        INPUT_TEMPFILE = tempfile.NamedTemporaryFile(delete=False,suffix=".csv") #create temporary file
        path= INPUT_TEMPFILE.name; INPUT_TEMPFILE.close()
        input_data.to_csv(path, index = False, header=True) #write DF to disk
    if typeOfData =="SOLUTION":
        #hay que descargar el catalogo si es necesario
        #cuando se añada SKYCDS el BKP_FOLDER se remplaza por el token del usuario
        # BKP_FOLDER = credentials['token_user']
        path = BKP_FOLDER+credentials['token_solution']+"/"+ credentials['task']+"/"
        if 'filename' in credentials:
            path+=credentials['filename']
        else:
            #tmp = os.listdir(path)
            tmp = [f for f in os.listdir(path) if not f.startswith('.')] #ignore hidden ones
            path +=tmp[0]
    elif typeOfData=="LAKE":
        path = GetWorkspacePath(credentials['token_user'],credentials['catalog']) + credentials['filename']
    elif typeOfData=="DUMMY": #no data, just a dummy file (is the easiest way to avoid an error, sorry in advance)
        text_for_test="WAKE ME UP, BEFORE YOU GO GO.."
        INPUT_TEMPFILE = tempfile.NamedTemporaryFile(delete=False,suffix=".txt") #create temporary file
        path = INPUT_TEMPFILE.name
        INPUT_TEMPFILE.write(text_for_test.encode())
        INPUT_TEMPFILE.close()
    else:
        path="."
    
    LOGER.error(path)
    name,ext = path.split("/")[-1].split(".") #get the namefile and then split the name and extention
    return path,name,ext


def GetWorkspacePath(tokenuser,workspace=None):
    #se creara el cataloog de fuentes de datos si es que no existe
    createFolderIfNotExist("%s%s" %(SPL_FOLDER,tokenuser))
    if workspace is None:
        return "%s%s/" %(SPL_FOLDER,tokenuser)
    else:
        createFolderIfNotExist("%s%s/%s" %(SPL_FOLDER,tokenuser,workspace)) #create folders of user and workspace
        return "%s%s/%s/" %(SPL_FOLDER,tokenuser,workspace)

    
#service to execute applications
def execute_service(service,metadata):
    f = open(metadata['data']['data'],"rb")
    control_number = metadata['DAG']['control_number']
    LOGER.info("Coordinator is executing...%s"% service)
    errors_counter=0
    ToSend = {'service':service,'context':NETWORK} #update status of falied node
    res = json.loads(ASK(params=ToSend))

    while(True): # AVOID ERRORS
        if res is None: #no more resources avaiable
            data= {'data':'','type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
            WARN(warn_message={'status':data['status'],"message":data["message"],"control_number":control_number,"label":"FALSE","task":metadata['DAG']['id'],"type":data['type'], "index":False}) #update status
            break
        LOGER.error(res)

        try:
            ip = res['ip']
            port = res['port']
        except KeyError as ke_ip:
            LOGER.error("Key error: %s" %ke_ip )
            LOGER.error(metadata['DAG'])
            data= {'data':'','type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
            WARN(warn_message={'status':data['status'],"message":data["message"],"control_number":control_number,"label":"FALSE","task":metadata['DAG']['id'],"type":data['type'], "index":False}) #update status
            break


        #send message to BB
        data = C.RestRequest(ip,port,metadata,data_file=f)

        if data is not None:
            LOGER.info(">>>>>>> SENT WITH NO ERRORS")
            errors_counter=0
            break
        else:
            errors_counter+=1
            LOGER.error(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
            if errors_counter>Tolerant_errors: #we reach the limit
                    ######## ASK AGAIN #######
                    ToSend = {'service':service,'context':NETWORK,'update':{'id':res['id'],'status':'DOWN','type':res['type']}} #update status of falied node
                    res = json.loads(ASK(params=ToSend))
                    errors_counter=0 #reset counter 
                    #------------------#
                    if 'info' in res: #no more nodes
                        res = None
                    else:
                        ip = res['ip'];port = res['port']
                        LOGER.error("TRYING A NEW NODE... IP:%s PORT: %s " %(ip,port) )
    LOGER.info("finishing execution...%s"% service)


app = Flask(__name__)

#root service
@app.route('/')
def prueba():
    return {"status":"OK","message":"xel is online."}

@app.route('/health',methods=['GET'])
def health():
    return json.dumps({"status":"OK"})

@app.route('/ADD', methods=['POST'])
def AddServiceResource():
    params = request.get_json(force=True)
    service = params['SERVICE']
    service_ID = params['ID']
    service_ip = params['IP']
    service_port = params['PORT']
    context = params['CONTEXT']
    
    ToSend={"id":service_ID,"ip":service_ip,"port":service_port,"context":context,"status":True,"workload":0} #status true is UP. False is down
    paxos_response = PROPOSER.Update_resource(service,service_ID,ToSend,read_action="ADD") # save request in paxos distributed memory

    return json.dumps(paxos_response)


@app.route('/ASK', methods=['POST'])
def ASK(params=None):
    if params is None:
        params = request.get_json(force=True)

    service = params['service'] #service name
    context = params['context']
    n=1 #quantity of workload added to resource
    force = True
    if 'force' in params: #option for gateways, gateways are forced to select a resource in the same context
        force = True
        n = 0

    if 'update' in params: #update node status
        info = params['update'] #{id,status,type}
        if info['status'] == "DOWN":
            PROPOSER.Update_resource(service,info['id'],{},read_action="DISABLE")

    res = PROPOSER.Read_resource(service,'',context,read_action="SELECT")['value'] #select

    if res is None: #no more avaiable resources
        return json.dumps({'info':'ERROR'})
    else:
        PROPOSER.Update_resource(service,res['id'],{},read_action="ADD_WORKLOAD")
        return json.dumps(res)


@app.route('/STATUS', methods=['GET'])
def services_status():
    services = PROPOSER.Read_resource('','','',read_action="STATUS")['value'] #select
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
def WARN(warn_message=None):
    if warn_message is None:
        warn_message = request.get_json(force=True)

    #ToSend={'status':status,"message":message,"label":label,"task":id_serv,"type":data_type, "index":index_opt} #update status
    control_number = warn_message['control_number']
    ######## paxos ##########
    paxos_response = PROPOSER.Update_task(control_number,warn_message) # save request in paxos distributed memory
    if paxos_response['status'] == "ERROR":
        LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
    #########################

    if 'times' in warn_message:
        tmp= warn_message['times']
        f = open(logs_folder+'log_'+control_number+'.txt', 'a+'); 
        #{"NAME":service_name,"ACQ":data_acq_time,"EXE":execution_time,"IDX":index_time}
        f.write("%s, %s, %s, %s \n" %(tmp['NAME'],tmp['ACQ'],tmp['EXE'],tmp['IDX'], )) 
        f.close()

    return json.dumps({'status':'OK'})


#service to execute a set of application in a DAG
@app.route('/executeDAG', methods=['POST'])
def execute_DAG():
    """
        {data_map:{data,type},DAG:{},token_solution(optional)}

        type:(LAKE,SOLUTION,RECORDS,SHARED,DUMMY)

        if SOLUTION: //local transversal, detect data produced by another solution from the same user 
            {data:{token_user,token_solution,task,filename(optional)},type:SOLUTION} #un catalogo del usuario
        if RECORDS: //raw data as records 
            {data:[],type:RECORDS}
        if LAKE: //obtained from a catalog in the CDN
            {data:{token_user,catalog(workspace),filename},type:LAKE}
        if SHARED: //shared transversal, detect data produced by another solution from another user 
            {data:{shared_token,task,filename(optional)},type:SHARED} #un catalogo del usuario
    """

    params = request.get_json(force=True)
    envirioment_params = params['auth'] #params wich define the enviroment  {user:,workspace:}
    data = params['data_map'] #data to be transform {data:,type:}
    DAG = json.loads(params['DAG']) #it have the parameters, the sub dag ,and the secuence of execution (its a json).
    
    LOGER.error(DAG)
    data_path,name,ext= GetDataPath(data) #get data path

    data['data'] = data_path
    data['type'] = ext

    LOGER.info(data_path)


    # verify if data exist
    if (os.path.exists(data['data'])):
        pass
    else:
        return {"status":"ERROR","message":"404: Data not found."}

    #A resquest random number for monitoring is created. 
    RN = CreateSolutionID(params)

    ######## paxos ##########
    paxos_response = PROPOSER.Save(RN,DAG,envirioment_params) # save request in paxos distributed memory
    if paxos_response['status'] == "ERROR":
        LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
        return {"status":"ERROR","message":"Mesh is not accepting requests"}
    #########################
    #Paxos returns the list of task tat will be executed. if list is void, then all the task have been executed before and must be pass the FORCE option to execute them again
    res = paxos_response['value']

    new_dag = res['DAG']
    task_list = res['task_list']
    is_already_running = res['is_already_running']
    if not is_already_running:
        for branch in new_dag:
            branch['control_number'] = RN
            if branch['id'] in task_list:
                parent = task_list[branch['id']]['parent']
                if parent is None or parent=="": #if service has no parent
                    LOGER.info(" service has no parent ")
                    path_bk_data = data_path
                    ext_bk_data = ext
                else:
                    LOGER.info(" ========= recovering data ========== Executing: %s with parent %s " % (branch['id'],parent) )
                    path_bk_data = "%s%s/%s" %(BKP_FOLDER,RN,parent)
                    tmp = [f for f in os.listdir(path_bk_data) if not f.startswith('.')] #ignore hidden ones
                    path_bk_data +="/"+tmp[0]
                    ext_bk_data = path_bk_data.split(".")[-1]
                    LOGER.info("recovering data from %s ..." % path_bk_data)

                data_format ={"data":path_bk_data,"type":ext_bk_data}
                metadata = {"data":data_format,"DAG":branch}
                service = branch['service'] #name of the service to send the instructions
                thread1 = Thread(target = execute_service, args = (service,metadata))
                thread1.start()
            else:
                LOGER.info(" ========= sending Raw data ========== ")

                metadata = {"data":data,"DAG":branch}
                service = branch['service']
                thread1 = Thread(target = execute_service, args = (service,metadata) )
                thread1.start()
                sleep(.5)
    else:
        LOGER.warning("Solution is already running")

    return json.dumps({"status":"OK",'token_solution':RN,"DAG":DAG,"is_already_running":is_already_running})

#service to monitoring a solution with a control number
@app.route('/monitor/v2/<token_project>/<token_solution>', methods=['GET'])
def monitoring_v2(token_project,token_solution):
    ######## paxos ##########
    paxos_response = PROPOSER.Consult_v2(token_project,token_solution) # consult request in paxos distributed memory
    #########################
    list_task = paxos_response['value']

    if list_task is None:
        return json.dumps({"status":"ERROR", "message":"Solution doesn't exist"})

    ToSend = {"status":"OK", "list_task": list_task,"additional_messages":[],"message":"Monitoring..."}
    for task, value in list_task.items():
        try:
            if 'DAG' in value: #el nodo fallo al estar procesando datos... se van a recuperar
                dag = value['DAG']
                parent = value['parent']
                path_bk_data = "%s%s/%s" %(BKP_FOLDER,token_solution,parent)
                tmp = [f for f in os.listdir(path_bk_data) if not f.startswith('.')] #ignore hidden ones

                path_bk_data +="/"+tmp[0]
                LOGER.info("recovering data %s ..." % path_bk_data)

                dag['control_number'] = token_solution # must be added, BB need it
                data ={"data":path_bk_data,"type":path_bk_data.split(".")[-1]}

                metadata = {"data":data,"DAG":dag}
                service = dag['service'] #name of the service to send the instructions

                thread1 = Thread(target = execute_service, args = (service,metadata))
                thread1.start()
                ToSend.additional_messages.append({"task":task, "status":"RECOVERING", "message":"RECOVERING DATA FROM %s" % task})

        except Exception as e:
            LOGER.error("No se pudieron recuperar los datos del dag")
            ToSend.additional_messages.append({"task":task, "status":"ERROR", "message":"task can not be recovered %s" % task})

    return ToSend

#service to monitoring a solution with a control number
@app.route('/monitor/<RN>', methods=['POST'])
def monitoring_solution(RN):
    #list of task
    sleep(1)
    ######## paxos ##########
    paxos_response = PROPOSER.Consult(RN) # consult request in paxos distributed memory
    #########################
    value = paxos_response['value']

    if value is None:
        return json.dumps({"status":"ERROR", "message":"Solution doesn't exist"})

    try:
        if 'DAG' in value: #el nodo fallo al estar procesando datos... se van a recuperar
            dag = value['DAG']
            parent = value['parent']

            path_bk_data = "%s%s/%s" %(BKP_FOLDER,RN,parent)
            #tmp = os.listdir(path_bk_data)
            tmp = [f for f in os.listdir(path_bk_data) if not f.startswith('.')] #ignore hidden ones

            path_bk_data +="/"+tmp[0]
            LOGER.info("recovering data %s ..." % path_bk_data)

            dag['control_number'] = RN # must be added, BB need it
            data ={"data":path_bk_data,"type":path_bk_data.split(".")[-1]}

            metadata = {"data":data,"DAG":dag}
            service = dag['service'] #name of the service to send the instructions

            thread1 = Thread(target = execute_service, args = (service,metadata))
            thread1.start()

            return json.dumps({"status":"INFO", "message":"RECOVERING DATA FROM %s" % service})


        if value is None:
            return json.dumps({"status":"ERROR", "message":"PAXOS ERROR"})
        else:
            return json.dumps(value) 
    except Exception as e:
        LOGER.info("No se pudieron recuperar los datos del dag")
        LOGER.info(dag)

        return json.dumps({"status":"ERROR", "message":"Task can not be recovered."})


#@app.route('/getdata/<RN>/<task>', methods=['POST'])
#def getdataintask(RN,task):
#    ######## paxos ##########
#    paxos_response = PROPOSER.Consult(RN,params={"task":task}) # consult request in paxos distributed memory
#    #########################
#
#    value = paxos_response['value']
#    if value is None:
#        return json.dumps({"status":"ERROR", "message":"PAXOS ERROR"})
#    else:
#        label = value['label']
#        data = GetIndexedData(label) #get data from label
#        if data['type'] == "csv":
#            newFile = open("tempfile.csv", "wb")
#            newFile.write(b64decode(data['data'].encode()))
#            newFile.close()
#
#        tempdf = pd.read_csv("tempfile.csv")
#        data['data'] = json.loads(tempdf.to_json(orient="records"))
#        return json.dumps({'status':"OK","data":data}) #no task found

@app.route('/getfile', methods=['POST'])
def getfileintask():
    """
    type:(LAKE,SOLUTION,RECORDS)
    if SOLUTION:
        {data:{token_user,token_solution,task,filename},type:SOLUTION} #un catalogo del usuario
    if LAKE:
        {data:{token_user,catalog(workspace),filename},type:LAKE}
    
    returns:
    {"status":"OK"/"ERROR", "message":"", "info":[] }

    """
    params = request.get_json(force=True)

    data_path,name,ext= GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
    file_exist=FileExist(data_path) #verify if data exist

    if file_exist:
        return send_file(
                data_path,
                as_attachment=True,
                attachment_filename="%s.%s" %(name,ext)
        )
    else:
        return {"status":"ERROR", "message":"file not found"}

## =============================================================== ##
## ========================== Solutions ========================== ##
## =============================================================== ##

@app.route('/solution/retrieve', methods=['POST'])
def retrieve_sol_from_DB():
    params = request.get_json(force=True)
    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
    token_solution = params['token_solution']
     ######## paxos ##########
    paxos_response = PROPOSER.Retrieve(token_solution,auth) # consult request in paxos distributed memory
    #########################
    return {"status":paxos_response['status'],"info":paxos_response['value']}    

@app.route('/solution/delete', methods=['POST'])
def delete_sol_from_DB():
    params = request.get_json(force=True)
    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
    token_solution = params['token_solution']
     ######## paxos ##########
    paxos_response = PROPOSER.Delete(token_solution,auth) # consult request in paxos distributed memory
    #########################
    return {"status":paxos_response['status'],"info":paxos_response['value']}    


@app.route('/solution/store', methods=['POST'])
def store_sol_in_DB():
    params = request.get_json(force=True)
    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
    metadata = params['metadata'] #metadata of the solution {name,desc,frontend}
    DAG = params['DAG'] #it have the parameters, the sub dag ,and the secuence of execution (its a json).
    #template = params['template'] #its almost the same as the dag, but is used for the GUI

    #token_solution = params['token_solution']
    token_solution = CreateSolutionID(params)
    
    ######## paxos ##########
    paxos_response = PROPOSER.Store(token_solution,DAG,metadata,auth) # consult request in paxos distributed memory
    #########################
    return {"status":paxos_response['status'], "message":paxos_response['value'],"info":{"token_solution":token_solution}}

@app.route('/solution/list', methods=['POST'])
def List_solutions_user():
    params = request.get_json(force=True)

    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}

    ######## paxos ##########
    paxos_response = PROPOSER.list_solutions(auth) # consult request in paxos distributed memory
    #########################
    return {"status":"OK", "info":paxos_response['value']}



## =============================================================== ##
## ========================= SOURCE DATA ========================= ##
## =============================================================== ##

@app.route('/workspace/create/<tokenuser>/<workspace>', methods=['GET'])
def create_workspace(tokenuser,workspace):
    GetWorkspacePath(tokenuser,workspace)
    return {"status":"OK"}

@app.route('/workspace/delete/<tokenuser>/<workspace>', methods=['GET'])
def delete_workspace(tokenuser,workspace):
    ws = GetWorkspacePath(tokenuser,workspace)
    shutil.rmtree(ws)
    return {"status":"OK"}

@app.route('/workspace/list/<tokenuser>', methods=['GET'])
def list_user_workspaces(tokenuser):
    path_workspaces= GetWorkspacePath(tokenuser)
    list_workspaces = [f for f in os.listdir(path_workspaces) if not f.startswith('.')] #ignore hidden ones

    return {"status":"OK", "info":{"workspaces":list_workspaces}}

@app.route('/workspace/list/<tokenuser>/<workspace>', methods=['GET'])
def list_userfiles_workspaces(tokenuser,workspace):
    path_workspace= GetWorkspacePath(tokenuser,workspace)
    list_of_files = [f for f in os.listdir(path_workspace) if not f.startswith('.')] #ignore hidden ones
    list_files_details = []
    for f in list_of_files:
        list_files_details.append(GetFileDetails(path_workspace+f,f))
    
    return {"status":"OK", "info":{"list_files_details":list_files_details}}

## =========== GET DATA ============ ##
@app.route('/workspace/getfile/<tokenuser>/<workspace>/<filename>', methods=['GET'])
def get_userfile_workspace(tokenuser,workspace,filename):
    data_path= GetWorkspacePath(tokenuser,workspace)+filename
    file_exist=FileExist(data_path) #verify if data exist
    if file_exist:
        binary_data = open(data_path,"rb").read()
    else:
        binary_data = 'File not found. sorry.'.encode()
    binary_data = b64decode(binary_data)
    return send_file(
                io.BytesIO(binary_data),
                as_attachment=True,
                attachment_filename=filename
        )


@app.route('/UploadDataset', methods=['POST'])
def UploadDataset():
    """
    function to upload to the catalog of user a dataset
    """
    f = request.files['file']
    filename = f.filename
    filetype = filename.split(".")[-1]

    workspace = request.form['workspace']
    tokenuser = request.form['user']

    # get worspace path
    workspace_path= GetWorkspacePath(tokenuser,workspace)
    f.save(os.path.join(workspace_path, filename)) #añadir DS al catalogo de fuentes de datos
    LOGER.info("Data saved in %s" % workspace_path+filename)

    return {"status":"OK"}

## =========== DELETE DATA ============ ##
@app.route('/workspace/delete/<tokenuser>/<workspace>/<filename>', methods=['GET'])
def delete_userfile(tokenuser,workspace,filename):
    data_path= GetWorkspacePath(tokenuser,workspace)+filename


    file_exist=FileExist(data_path) #verify if data exist
    if file_exist:
        os.remove(data_path)
        # se borra tambien el archivo desc.json
        name,ext = data_path.split("/")[-1].split(".")
        desc_file_path = data_path.replace("%s.%s" %(name,ext),".%s_desc.json" %(name))
        os.remove(desc_file_path)
    return {"status":"OK"}

## =============================================================== ##
## =========================== RESULTS =========================== ##
## =============================================================== ##

@app.route('/ArchiveData/<RN>/<task>', methods = ['POST'])
def upload_file(RN,task):
    tmp_f = createFolderIfNotExist("%s/" % RN,wd=BKP_FOLDER)
    path_to_archive= createFolderIfNotExist("%s/" % task,wd=tmp_f)
    f = request.files['file']
    filename = f.filename
    f.save(os.path.join(path_to_archive, filename))
    return json.dumps({"status":"OK", "message":"OK"})


@app.route('/DatasetQuery', methods=['POST'])
def queryDS():
    """
    type:(LAKE,SOLUTION,RECORDS)
    if SOLUTION:
        {data:{token_user,token_solution,task,filename},type:SOLUTION,ask:[]} #un catalogo del usuario
    if LAKE:
        {data:{token_user,catalog(workspace),filename},type:LAKE,ask:[]}

    ask : {request:"", value:"" }
        request values:
            -unique
            -query
            -inside 

    returns:
    {"status":"OK"/"ERROR", "message":"", "info":[] }

    """
    params = request.get_json(force=True)
    ask_list = params['ask']
    data_path,name,ext= GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
    LOGER.info("Data must be in %s " % data_path)
    file_exist=FileExist(data_path) #verify if data exist

    response={"status":"OK","message":"","info":[]}

    if file_exist and ext=="csv":
        results = Request2Dataset(data_path,ask_list)
        response['info']=results
        #LOGER.info(response)

    return json.dumps(response)



@app.route('/DescribeDataset/v2', methods=['POST'])
def describeDatasetv2():
    """
    function to describe a dataset un users catalog or results of a task in a solution
    
    type:(LAKE,SOLUTION,RECORDS)
    if SOLUTION:
        {data:{token_user,token_solution,task,filename},type:SOLUTION} #un catalogo del usuario
    if RECORDS:
        {data:[],type:RECORDS}
    if LAKE:
        {data:{token_user,catalog(workspace),filename},type:LAKE}

    returns:
    {"status":"OK"/"ERROR", "message":"", "info":{"parent_filename":<name_of_original_file>,"list_of_files":[<list of names>],","files_info":{<file_name>:{} }}}
    """
    def verify_extentions(data_path,ext,response,filename,delimiter=","):
        valid = False #flag to mark a valid file
        if ext=="zip":
            valid=True
            dirpath,list_of_files=zip_extraction(data_path)
            for fname in list_of_files:
                fext = GetExtension(fname)
                response,file_validation = verify_extentions(dirpath+"/"+fname,fext,response,fname,delimiter) #recursive
            response['info']['tree'] = CreateFilesTree(list_of_files)
            
            # must delete the temp folder
            shutil.rmtree(dirpath)

        elif ext =="folder": #if its a folder #creo que nisiquiera se requiere
            valid=True
            list_of_files = listdir("%s/%s"%(data_path,filename))
            for f in list_of_files:
                LOGER.error(f)
                fname = "%s/%s" %(filename,f)
                fext = GetExtension(fname)
                response,file_validation = verify_extentions(dirpath+"/"+fname,fext,response,fname,delimiter) #recursive

        elif ext=="csv":  #describe csv
            enc = detect_encode(data_path)
            LOGER.info(enc)
            dataset= pd.read_csv(data_path,encoding=enc['encoding'],sep=delimiter)
            #LOGER.info(dataset)
            response['info']['files_info'][filename] = DatasetDescription(dataset)
            response['info']['list_of_files'].append(filename)
            # normalize to utf and separated by ,
            dataset.to_csv(data_path,encoding='utf-8-sig',index=False)

            valid=True

        elif ext=="json":
            dataset = pd.read_json(data_path)
            response['info']['files_info'][filename] = DatasetDescription(dataset)
            response['info']['list_of_files'].append(filename)
            valid=True
        return response,valid 

    init = time.time()
    params = request.get_json(force=True)
    if 'force' in params:
        force_desc = True
    else:
        force_desc= False

    separator = params['delimiter']
    try:
        data_path,name,ext= GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
    except ValueError as VE:
        return {"status":"ERROR","message":"Invalid filename"}
    LOGER.info("Data must be in %s " % data_path)

    file_exist=FileExist(data_path) #verify if data exist
    desc_file_path = data_path.replace("%s.%s" %(name,ext),".%s_desc.json" %(name))
    desc_file_exist=FileExist(desc_file_path)

    filename = "%s.%s" %(name,ext)
    response={"status":"OK","message":"","file_exist":file_exist,"info":{"parent_filename":filename,"list_of_files":[],"files_info":{}}}

    if file_exist:
        if desc_file_exist and force_desc is False: #load the exiting description
            response = json.load(open(desc_file_path))
        else:
            response,file_validation=verify_extentions(data_path,ext,response,filename,delimiter=separator)
            if file_validation: #save in file
                with open(desc_file_path,'w') as f:
                    f.write(json.dumps(response))
            else:
                response['status']="ERROR"
                response['message']="Datafile can't be described. Try with the following file extentions:csv,json, or zip."

    LOGER.info(init-time.time())
    return jsonify(response)




@app.route('/getlog/<RN>', methods=['GET'])
def getLogFile(RN):
    return send_file(logs_folder+'log_'+RN+'.txt',as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555,debug = True) #for development
    #serve(app, host='0.0.0.0', port=5555)

