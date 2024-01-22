from cgitb import reset
import sys,os,ast
import pandas as pd
from threading import Thread
from flask import Flask,request,jsonify,send_file,make_response
from waitress import serve

import json
from time import sleep
import C
import logging #logger
from base64 import b64encode,b64decode
import io
import tempfile
import shutil
import time
from os import listdir


# local imports
from functions import *
from Proposer import Paxos
from Auth import login_request, register_user, token_required,data_autorization_requiered, resource_autorization_requiered,API_required,logout_request
from BB_dispatcher import bb_dispatcher 
from PostmanPaxos import postman
from DataGarbageCollector import GarbageCollector
from FSController import FSController,MessageController

import genesis_client as GC


########## GLOBAL VARIABLES ##########
dictionary = dict()
with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services

logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMESH" #equivalente a catalogo en skycds, es decir, una solucion o un DAG
#TPSHOST ="http://tps_manager:5000"
NETWORK=os.getenv("NETWORK") 
MODE=os.getenv("MODE") 
REMOTE_STORAGE=TranslateBoolStr(os.getenv("REMOTE_STORAGE"))
if REMOTE_STORAGE:
    from storage.mictlanx_client import mictlanx_client
    STORAGE_CLIENT = mictlanx_client()
else:
    STORAGE_CLIENT = None



ALLOW_REGISTER_NEW_USERS= TranslateBoolStr(os.getenv("ALLOW_REGISTER_NEW_USERS"))
INIT_EXAMPLE = TranslateBoolStr(os.getenv("INIT_EXAMPLE")) 
DEBUG_MODE = TranslateBoolStr(os.getenv("DEBUG_MODE"))


DATASET_EXAMPLES_FOLDER="./examples/datasets/"
DAG_EXAMPLES_FOLDER="./examples/dags/"
REFERENCES_FOLDER="./references/"


TIMES_list = {}

FS = FSController(LOGER=LOGER,CLOUD=STORAGE_CLIENT,REMOTE_STORAGE=REMOTE_STORAGE)

#select load blaancer
Tolerant_errors=0 #total of errors that can be tolarated
ACCEPTORS_LIST= dictionary['paxos']["accepters"]
LOGER.info(ACCEPTORS_LIST)
PROPOSER = Paxos(ACCEPTORS_LIST)

# Garbage collector para backups
#GarbageColl = GarbageCollector(PROPOSER,BKP_FOLDER,LOGER,stopwatch=120)
#GarbageColl.start()
########## END GLOBAL VARIABLES ##########


def GetPostman(service=None,hash_product=""):
    return postman(PROPOSER,FS.GetFolder("RESULTS"),service=service,LOGER=LOGER,hash_product=hash_product)

def init_user(user,password):
    if INIT_EXAMPLE:
        #login
        resp = login_request(user,password)
        userinfo = json.loads(resp.get_data(as_text=True))
        tokenuser = userinfo['data']['tokenuser']
        access_token = userinfo['data']['access_token']
        logout_request(tokenuser,access_token)
        defaulth_path= FS.GetWorkspacePath(tokenuser,"Default")
        examples_path= FS.GetWorkspacePath(tokenuser,"Examples")
        shutil.copytree(DATASET_EXAMPLES_FOLDER,examples_path,dirs_exist_ok=True) #copy datasets
        
        #load dags
        dags = os.listdir(DAG_EXAMPLES_FOLDER)
        for dag in dags:
            dag_obj = json.load(open(DAG_EXAMPLES_FOLDER+dag))

            token_solution = CreateSolutionID({})
            dag_obj['metadata']['token'] = token_solution
            dag_obj['metadata']['datasource']['token_user'] = tokenuser
            dag_obj['metadata']['datasource']['catalog'] = "Examples"

            ######## paxos ##########
            PROPOSER.Store(token_solution,json.dumps(dag_obj['dataobject']),dag_obj['metadata'],{"user":tokenuser,"workspace":"Examples"})
            ####################

    return 0

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
                LOGER.debug(f)
                fname = "%s/%s" %(filename,f)
                fext = GetExtension(fname)
                response,file_validation = verify_extentions(dirpath+"/"+fname,fext,response,fname,delimiter) #recursive

        elif ext=="csv":  #describe csv
            enc = detect_encode(data_path)
            #LOGER.info(enc)
            #LOGER.info(delimiter)
            dataset= pd.read_csv(data_path,encoding=enc['encoding'],sep=delimiter)
            #LOGER.info(dataset)
            response['info']['files_info'][filename] = DatasetDescription(dataset)
            response['info']['list_of_files'].append(filename)
            # normalize to utf and separated by ,
            dataset.to_csv(data_path,encoding='utf-8-sig',index=False)
            del dataset
            valid=True

        elif ext=="json":
            try:
                dataset = pd.read_json(data_path)
                response['info']['files_info'][filename] = DatasetDescription(dataset)
                valid=True
                del dataset
            except Exception as e:
                LOGER.error("imposible to get info")
            
            response['info']['list_of_files'].append(filename)
        else:
            response['info']['list_of_files'].append(filename)
        
        return response,valid 




#service to execute applications
def execute_service(parent,metadata,include_hash=False):
    postman = GetPostman()

    if include_hash:
        postman.calculate_sha256sum(metadata['data']['data'])

    f = open(metadata['data']['data'],"rb")
    control_number = metadata['DAG']['control_number']

    dispatcher = bb_dispatcher(control_number,parent,control_number,LOGER=LOGER,POSTMAN=postman,Tolerant_errors=Tolerant_errors)
    dispatcher.Send_to_BB(metadata['data'],f,metadata['auth'], metadata['DAG'])
   

app = Flask(__name__)

#root service
@app.route('/')
@token_required
def prueba():
    return {"status":"OK","message":"xel is online."}

@app.route('/health',methods=['GET'])
def health():
    return json.dumps({"status":"OK"})

@app.route('/signup',methods=['POST'])
def signup():
    if ALLOW_REGISTER_NEW_USERS:
        params = request.get_json(force=True)
        resp = register_user(params['username'],params['email'],params['password'])
        if resp.status_code==201: #if user was created, then initialize it.
            init_user(params['username'],params['password'])

        return resp
        
    return {"status":"ERROR","message":"Registration is blocked"}

@app.route('/login',methods=['POST'])
def login_access():
    params = request.get_json(force=True)
    return login_request(params['user'],params['password'])

@app.route('/logout',methods=['POST'])
def close_session():
    params = request.get_json(force=True)
    return logout_request(params['tokenuser'],params['access_token'])

@app.route('/ADD', methods=['POST'])
@token_required
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
@token_required
def ASK():
    params = request.get_json()
    postman = GetPostman()
    return postman.AskGateway(params)

@app.route('/STATUS', methods=['GET'])
@token_required
def services_status():
    services = PROPOSER.Read_resource('','','',read_action="STATUS")['value'] #select
    return jsonify(services)

@app.route('/report_time', methods=['POST'])
@token_required
def append_log():
    params = request.get_json(force=True)
    tmp= params['times'] #id,acq,serv,trans,exec,idx,comm
    token_solution = params['token_solution']

    FS.write_time_log(tmp,token_solution)
    
    return json.dumps({'status':'OK'})

@app.route('/WARN', methods=['POST'])
@token_required
def WARN():
    warn_message = request.get_json(force=True)
    postman = GetPostman()
    LOGER.error(warn_message)
    return postman.WarnGateway(warn_message)

@app.route('/stopDAG/<token_project>/<token_solution>', methods=['GET'])
@token_required
def stop_DAG(token_project,token_solution):
    GC.remove_services(token_solution) #force stop
    paxos_response = PROPOSER.Consult_v2(token_project,token_solution,None,kind_task="task_list",force_stop_healthcheck=True) # consult request in paxos distributed memory
    make_response({"status":"OK","message":"solution stopped"},200)    

#service to deploy service stack
@app.route('/deploy', methods=['POST'])
@token_required
@resource_autorization_requiered
def deploy_resources():
    """
        {DAG:{},token_solution(optional),auth:{}}
    """
    params = request.get_json(force=True)
    envirioment_params = params['auth'] #params wich define the enviroment  {user:,workspace:}
    DAG = json.loads(params['DAG']) #it have the parameters, the sub dag ,and the secuence of execution (its a json).

    Alias = params['alias'] if 'alias' in params else 'default'
    meta = params['metadata'] if 'metadata' in params else {}
    dataobject = params['dataobject'] if 'dataobject' in params else None

    RN = CreateSolutionID(params)
    TIMES_list[RN]={"deploy":0,"total":time.time(),"recovery":0,"alias":Alias}

    exec_options = {}
    if 'options' in params:
        exec_options = params['options'] 
        if 'force' in exec_options:
            exec_options['force'] = TranslateBoolStr(exec_options['force'])
    
    exec_options['justdeploy'] =True

    ######## paxos ##########
    paxos_response = PROPOSER.Save(RN,DAG,envirioment_params,metadata=meta,options=exec_options,dataobject=dataobject) # save request in paxos distributed memory
    if paxos_response['status'] == "ERROR":
        LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
        return make_response({"status":"ERROR","message":"Mesh is not accepting requests"},503)
    #########################
    #Paxos returns the list of task tat will be executed. if list is void, then all the task have been executed before and must be pass the FORCE option to execute them again
    res = paxos_response['value']

    ###################### DEPLOY SERVICES #########################
    if MODE == "SERVERLESS" and len(res['DAG'])>0:
        temp = time.time()
        GC.start_services({
                "DAG":res['DAG'],
                "id_stack": RN,
                "mode":"compose",
                "engine":"nez",
                "replicas": 2})
        LOGER.info("---------------------------- DEPLOYED")

        TIMES_list[RN]['deploy'] = time.time() - temp
        time.sleep(.5)
        response = make_response({"status":"OK","message":"solution deployed",'token_solution':RN,"dag":res['DAG']},200)    
    else:
        response = make_response({"status":"OK","message":"No more nodes needed",'token_solution':RN,"dag":res['DAG']},200)    
    ################################################################
    return response

@app.route('/removestack', methods=['POST'])
@token_required
@resource_autorization_requiered
def remove_deployed_stack():
    params = request.get_json(force=True)
    token_solution = params['token_solution']

    response = make_response({"status":"OK","message":"stack not found"},200)    
    try:
        if MODE == "SERVERLESS": #stop containers
            if not DEBUG_MODE:
                LOGER.error("STOPING CONTAIENRS")
                GC.remove_services(token_solution)
                PROPOSER.Update_resource('','',{"context":token_solution},read_action="CONTEXT_DOWN")
                response = make_response({"status":"OK","message":"stack removed"},200)    
    except Exception as e:
        LOGER.error(e)
    return response

@app.route('/exec', methods=['POST'])
@token_required
def exec_func():
    """
    {resource:"",params:{}(optional)}
    
    also, must attach data in "file"
    """

    f = request.files['file']
    filename = f.filename
    filetype = filename.split(".")[-1]

    params = request.get_json(force=True)
    resource = params['resource'] if 'resource' in params else "funxion"
    parameters = params['params'] if 'params' in params else {}
    

#service to execute a set of applications in a DAG
@app.route('/executeDAG', methods=['POST'])
@token_required
@resource_autorization_requiered
def execute_DAG():
    """
        {data_map:{data,type},DAG:{},token_solution(optional),auth}

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
    meta = params['metadata'] if 'metadata' in params else {}
    dataobject = params['dataobject'] if 'dataobject' in params else None

    RN = CreateSolutionID(params)    #A resquest random number for monitoring is created. 

    exec_options = {}
    if 'options' in params:
        exec_options = params['options'] 
        if 'force' in exec_options:
            exec_options['force'] = TranslateBoolStr(exec_options['force'])
            
            if exec_options['force']:#force run
                FS.clean_results_dir(RN) #clean dir with results


    data_path,name,ext= FS.GetDataPath(data) #get data path

    # verify if data exist
    if not (FileExist(data_path)):
        return make_response({"status":"ERROR","message":"404: Data not found."},406)

    MC = MessageController(DAG,RN,envirioment_params,LOGER=LOGER)
    MC.AssignDataMap(data_path,ext)

    ######## paxos ##########
    paxos_response = PROPOSER.Save(RN,DAG,envirioment_params,metadata=meta,options=exec_options,dataobject=dataobject) # save request in paxos distributed memory
    if paxos_response['status'] == "ERROR":
        LOGER.error("PAXOS PROTOCOL DENIED THE REQUEST")
        return make_response({"status":"ERROR","message":"Mesh is not accepting requests"},503)
    #########################
    #Paxos returns the list of task tat will be executed. if list is void, then all the task have been executed before and must be pass the FORCE option to execute them again
    res = paxos_response['value']

    new_dag = res['DAG']
    task_list = res['task_list']
    is_already_running = res['is_already_running']

    if not is_already_running:
        dispatcher_parent = '' # is void if coordinator is the parent
        for branch in new_dag:
            branch['control_number'] = RN
            if branch['id'] in task_list:
                parent = task_list[branch['id']]['parent']
                if parent is None or parent=="": #if service has no parent
                    LOGER.info(" service has no parent ")
                    data_map = MC.GetDataMap()
                else:
                    LOGER.info(" ========= recovering data ========== Executing: %s with parent %s " % (branch['id'],parent) )
                    data_map = FS.RecoverDataFromtask(RN,parent)
                    dispatcher_parent = parent
 
                metadata = MC.CreateXelRequest(data_map,branch,envirioment_params)
                thread1 = Thread(target = execute_service, args = (dispatcher_parent,metadata,True))
                thread1.start()
            else:
                LOGER.info(" ========= sending Raw data ========== ")
                metadata = MC.CreateXelRequest(MC.GetDataMap(),branch,envirioment_params)
                thread1 = Thread(target = execute_service, args = (dispatcher_parent,metadata,True) )
                thread1.start()
                sleep(.5)
    else:
        LOGER.warning("Solution is already running")

    return make_response({"status":"OK",'token_solution':RN,"DAG":DAG,"is_already_running":is_already_running},202)

#service to monitoring a solution with a control number
@app.route('/monitor/v2/<token_project>/<token_solution>', methods=['POST','GET'])
@token_required
def monitoring_v2(token_project,token_solution):
    tasks = None
    kind_task = "task_list" #subtask
    show_history=None
    MC = MessageController(None,token_solution,None,LOGER=LOGER)

    if request.method == 'POST':
        params = request.get_json(force=True)
        if "tasks" in params:
            tasks = params['tasks']
        if "kind_task" in params:
            kind_task = params['kind_task']
        if "show_history" in params:
            show_history = params['show_history']

    ######## paxos ##########
    paxos_response = PROPOSER.Consult_v2(token_project,token_solution,tasks,kind_task=kind_task,show_history=show_history) # consult request in paxos distributed memory
    #########################
    response = paxos_response['value']

    if response is None:
        return make_response({"status":"ERROR", "message":"Solution doesn't exist"},404)
    
    list_task = response['tasks']
    solution_status = response['solution']

    ToSend = {"status":"OK", "list_task": list_task,"message":"Monitoring..."}
    ToSend['additional_messages']=[]
    for task, value in list_task.items():
        try:
            if 'DAG' in value: #el nodo fallo al estar procesando datos... se van a recuperar
                temp = time.time()
                dag = value['DAG']
                parent = value['parent']
                data_map = FS.RecoverDataFromtask(token_solution,parent)

                LOGER.info("========================================================================================")
                LOGER.info("============================ recovering data %s ========================" % data_map['data'])
                LOGER.info("========================================================================================")
                dag['control_number'] = token_solution # must be added, BB need it
                metadata = MC.CreateXelRequest(data_map,dag,{"user":token_project,"workspace":"not important"})

                thread1 = Thread(target = execute_service, args = (parent,metadata))
                thread1.start()
                ToSend['additional_messages'].append({"task":task, "status":"RECOVERING", "message":"RECOVERING DATA FROM %s" % task})
                TIMES_list[token_solution]['recovery'] += time.time() - temp


        except Exception as e:
            LOGER.error("No se pudieron recuperar los datos del dag")
            ToSend['additional_messages'].append({"task":task, "status":"ERROR", "message":"task can not be recovered %s" % task})


    if solution_status['status']=="FAILED" or solution_status['status']=="FINISHED":
        if token_solution in TIMES_list:
            TIMES_list[token_solution]['total'] = time.time() - TIMES_list[token_solution]['total']
            FS.write_solution_log(TIMES_list[token_solution],token_solution)
            del TIMES_list[token_solution]

    return make_response(ToSend,200)

## =============================================================== ##
## =========================== Metadata ========================== ##
## =============================================================== ##
@app.route('/ProductsObjectMap', methods=['POST'])
@token_required
def ProductsObjectMap():
    obj_request = request.get_json(force=True)
    paxos_response = PROPOSER.DirectRequest(obj_request,request="PRODUCTS_MAP")

    if paxos_response['status']=="OK":
        return make_response(paxos_response,200)   
    else:
        return make_response(paxos_response,404)   

@app.route('/Validate_subtask_executions', methods=['POST'])
@token_required
def Validate_subtask_execution():
    obj_request = request.get_json(force=True)
    paxos_response = PROPOSER.DirectRequest(obj_request,request="VALIDATE_SUBTASK_EXE")

    if paxos_response['status']=="OK":
        return make_response(paxos_response,200)   
    else:
        return make_response(paxos_response,404)   

## =============================================================== ##

@app.route('/getfile', methods=['POST'])
@token_required
@data_autorization_requiered
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
    try:
        params = request.get_json(force=True)
        data_path,name,ext= FS.GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
        file_exist=FileExist(data_path) #verify if data exist
        #LOGER.error(data_path)

        if file_exist:
            return send_file(
                    data_path,
                    as_attachment=True,
                    download_name="%s.%s" %(name,ext) #attachment_filename
            )
        else:
            return make_response({"status":"ERROR", "message":"file not found"},404)
    except Exception as e:
        LOGER.error(e)
        return make_response({"status":"ERROR", "message":"file not found"},404)

## =============================================================== ##
## ========================== Solutions ========================== ##
## =============================================================== ##

@app.route('/solution/retrieve', methods=['POST'])
@token_required
@resource_autorization_requiered
def retrieve_sol_from_DB():
    params = request.get_json(force=True)
    try:
        auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
        token_solution = params['token_solution']
        ######## paxos ##########
        paxos_response = PROPOSER.Retrieve(token_solution,auth) # consult request in paxos distributed memory
        #########################
        return make_response({"status":paxos_response['status'],"info":paxos_response['value']},200)
    except:
        return make_response({"message":"invalid token solution"},404)

@app.route('/solution/delete', methods=['POST'])
@token_required
@resource_autorization_requiered
def delete_sol_from_DB():
    try:
        params = request.get_json(force=True)
        auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
        token_solution = params['token_solution']
        ######## paxos ##########
        paxos_response = PROPOSER.Delete(token_solution,auth) # consult request in paxos distributed memory
        solution_path = FS.GetSolutionPath(token_solution)
    except:
        return make_response({"message":"invalid token solution"},404)

    try:
        shutil.rmtree(solution_path)
    except Exception as e:
        LOGER.info("No se requiere borrar un directorio")
        
    #########################
    return make_response({"status":paxos_response['status'],"info":paxos_response['value']},200)    


@app.route('/solution/store', methods=['POST'])
@token_required
@resource_autorization_requiered
def store_sol_in_DB():
    try:
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
        return make_response({"status":paxos_response['status'], "message":paxos_response['value'],"info":{"token_solution":token_solution}},200)
    except:
        return make_response({"message":"invalid token solution"},404)

@app.route('/solution/list', methods=['POST'])
@token_required
@resource_autorization_requiered
def List_solutions_user():
    try:
        params = request.get_json(force=True)
        auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
        query=None
        if 'params' in params:
            query = params['params']
        ######## paxos ##########
        paxos_response = PROPOSER.list_solutions(auth,query) # consult request in paxos distributed memory
        #########################
        return make_response({"status":"OK", "info":paxos_response['value']},200)
    except:
        return make_response({"message":"invalid token solution"},404)


## =============================================================== ##
## ========================= SOURCE DATA ========================= ##
## =============================================================== ##

@app.route('/workspace/create/<tokenuser>/<workspace>', methods=['GET'])
@token_required
def create_workspace(tokenuser,workspace):
    FS.GetWorkspacePath(tokenuser,workspace)
    return {"status":"OK"}

@app.route('/workspace/delete/<tokenuser>/<workspace>', methods=['GET'])
@token_required
def delete_workspace(tokenuser,workspace):
    FS.DeleteWorkspace(tokenuser,workspace)
    return {"status":"OK"}

@app.route('/workspace/list/<tokenuser>', methods=['GET'])
@token_required
def list_user_workspaces(tokenuser):
    list_workspaces = path_workspaces= FS.GetAllWorkspaces(tokenuser)
    return {"status":"OK", "info":{"workspaces":list_workspaces}}

@app.route('/workspace/list/<tokenuser>/<workspace>', methods=['GET'])
@token_required
def list_userfiles_workspaces(tokenuser,workspace):
    list_files_details= FS.ListFilesWorkspace(tokenuser,workspace)
    return {"status":"OK", "info":{"list_files_details":list_files_details}}

## =========== GET DATA ============ ##
@app.route('/workspace/getfile/<tokenuser>/<workspace>/<filename>', methods=['GET'])
@token_required
def get_userfile_workspace(tokenuser,workspace,filename):
    binary_data  = FS.GetFileWorkspace(tokenuser,workspace,filename)
    return send_file(
                io.BytesIO(binary_data),
                as_attachment=True,
                attachment_filename=filename
        )


@app.route('/UploadDataset', methods=['POST'])
@token_required
def UploadDataset():
    """
    function to upload to the catalog of user a dataset
    """
    f = request.files['file']
    filename = f.filename
    workspace = request.form['workspace']
    tokenuser = request.form['user']

    # get worspace pathGetWorkspacePath
    workspace_path= FS.GetWorkspacePath(tokenuser,workspace)
    f.save(os.path.join(workspace_path, filename)) #añadir DS al catalogo de fuentes de datos
    #LOGER.info("Data saved in %s" % workspace_path+filename)
    return make_response({"status":"OK"},200) 

@app.route('/CreatePackage', methods=['POST'])
@token_required
def CreatePackage():
    """
    function to create a zip with csv in the LAKE
    {
        "tokenuser":<tokenuser>
        "name_package":"fusion_AandB"
        "list_files":["<workspace>/<filename>","<workspace>/<filename>","<workspace>/<filename>"],
        "destination":<workspace>,
        "force_cration":true/false
        
    }
    return: ::: {"status":"OK", "filename":<filename>}
    """
    params = request.get_json(force=True)
    list_paths= []
    # verify if zip already exist
    destination = FS.GetWorkspacePath(params['tokenuser'],params['destination'])

    file_exist=FileExist(destination+params['name_package']) #verify if data exist
    if not file_exist or params['force_cration']:

        for Pathfile in params["list_files"]:
            workspace,filename=Pathfile.split("/")
            list_paths.append(FS.GetWorkspacePath(params['tokenuser'],workspace)+filename)

        zip_creation(list_paths,params['name_package'],destination)

    return make_response({"status":"OK", "filename":params['name_package']+".zip"},200)



## =========== DELETE DATA ============ ##
@app.route('/workspace/delete/<tokenuser>/<workspace>/<filename>', methods=['GET'])
@token_required
def delete_userfile(tokenuser,workspace,filename):
    data_path= FS.GetWorkspacePath(tokenuser,workspace)+filename

    file_exist=FileExist(data_path) #verify if data exist
    if file_exist:
        os.remove(data_path)
        # se borra tambien el archivo desc.json
        name,ext = data_path.split("/")[-1].split(".")
        desc_file_path = data_path.replace("%s.%s" %(name,ext),".%s_desc.json" %(name))
        descfile_exist=FileExist(desc_file_path) #verify if data exist
        if descfile_exist:
            os.remove(desc_file_path)

    return make_response({"status":"OK"},200)

## =============================================================== ##
## =========================== RESULTS =========================== ##
## =============================================================== ##

@app.route('/ArchiveData/<token_solution>/<task>', methods = ['POST'])
@API_required
def upload_file(token_solution,task):
    #LOGER.debug("INDEX DATA to %s" %RN)
    metadata = json.loads(request.cookies['metadata']) if 'metadata' in request.cookies else {"product_name":"product"}

    FS.StoreResult(request,token_solution,task)

    #SAVE LIST OF PRODUCTS IN DB AVOIDING 
    meta = getMetadataFromPath(task,as_list=False)
    meta["product_name"] = metadata["product_name"] if 'product_name' in metadata else "dataset/product"
    meta["id"] = task 
    meta["token_solution"] = token_solution 

    paxos_response = PROPOSER.DirectRequest(meta,request="INSERT_PRODUCT")

    return json.dumps({"status":"OK", "message":"OK"})



@app.route('/metadata/get/<token_solution>', methods = ['GET'])
def get_all_metadata_products(token_solution):
    paxos_response = PROPOSER.DirectRequest({"token_solution":token_solution,"query":{}},request="GETALL_PRODUCTS")
    
    log_products = pd.DataFrame.from_records(paxos_response['value']) #data is now a dataframe
    log_products.to_csv("%s/%s/list_products.csv" %(FS.GetFolder("RESULTS"),token_solution),index=False)
    if paxos_response['status']=="OK":
        return make_response(paxos_response,200)   
    else:
        return make_response(paxos_response,404)   



@app.route('/locate/<RN>/<task>', methods = ['GET'])
def locate_file_in_remote_storage(RN,task):
    #LOGER.info("LOCALIZANDO!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")
    token_data = CreateDataToken(RN,task)
    url_data_resouce= ""
    if REMOTE_STORAGE:
        url_data_resouce = STORAGE_CLIENT.locate(token_data)

    return json.dumps({"status":"OK", "message":"OK","location":url_data_resouce})

@app.route('/DatasetQuery', methods=['POST'])
@token_required
@data_autorization_requiered
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
    params = request.get_json()
    ask_list = params['ask']
    data_path,name,ext= FS.GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
    file_exist=FileExist(data_path) #verify if data exist

    response={"status":"OK","message":"","info":[]}

    if file_exist and ext=="csv":
        results = Request2Dataset(data_path,ask_list)
        response['info']=results

    return make_response(response,200) #dump



@app.route('/DescribeDataset/v2', methods=['POST'])
@token_required
@data_autorization_requiered
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

    init = time.time()
    params = request.get_json(force=True)

    force_desc = True if 'force' in params else False

    separator = params['delimiter']
    try:
        data_path,name,ext= FS.GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
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
            with open(desc_file_path) as f:
                response = json.load(f)
        else:
            response,file_validation=verify_extentions(data_path,ext,response,filename,delimiter=separator)
            if file_validation: #save in file
                with open(desc_file_path,'w') as f:
                    f.write(json.dumps(response))
            else:
                response['status']="ERROR"
                response['message']="Datafile can't be described. Try with the following file extentions:csv,json, or zip."

    LOGER.info(init-time.time())
    return make_response(response,200)


@app.route('/reference/get', methods=['POST'])
def GetReference():
    """
    query = table.query
    Mundial=@{$REF::ref_incidencia_both_mexico.$VAR::descripcion}
    """
    params = request.get_json()
    table = params['query'] #tabla
    env_params = params['ENV']

    #leer el mapa de variables de interes
    with open('%sreferencesIV.json' % (REFERENCES_FOLDER) ) as json_file:
        IVRef = json.load(json_file) #read all configurations for services
    
    if table not in IVRef:
        return make_response({"status":"ERROR","message":"not in database"},404)    

    data_path = "%s%s" % (REFERENCES_FOLDER,FormatCommand(IVRef[table]["path"], env_params))
    data_path= data_path.replace(">","+")
    LOGER.info("data path de la referencia corregido: %s" % data_path)

    file_exist=FileExist(data_path) #verify if data exist
    if file_exist:
        ref_dataset = pd.read_csv(data_path)
        queryValue="0"

        if IVRef[table]["mode"] == "range": #IF RANGE
            queryValue =int(env_params[IVRef[table]['code']][1:]) if IVRef[table]["RemoveFirstLetter"] else env_params[IVRef[table]['code']] #aqui el str puede causar error
            ref_dataset[['min_col', 'max_col']] = ref_dataset[IVRef[table]["range_col"]].str.split(IVRef[table]["sep"], expand=True)
            ref_dataset['max_col'].fillna(ref_dataset['min_col'], inplace=True)
            columnas_a_convertir = ["max_col", "min_col"]
            ref_dataset[columnas_a_convertir] = ref_dataset[columnas_a_convertir].apply(pd.to_numeric, errors='coerce')
            filtro =  (ref_dataset["min_col"] <= queryValue) & (ref_dataset["max_col"] >= queryValue)
            ref_dataset = ref_dataset[filtro].reset_index()

            #LOGER.info(ref_dataset)
            #LOGER.error("any fitlered value: %s " % filtro.any())
        
        if ref_dataset.empty:
            ref_value = 0
        else:
            ref_value = ref_dataset[IVRef[table]["VI"]][0]

        LOGER.info("reference value: %s ; key: %s" % (ref_value,queryValue ))
        return make_response({"status":"OK","message":"reference found","value": ref_value},200)    
    else:
        return make_response({"status":"ERROR","message":"not found"},404)    



@app.route('/getlog/<RN>', methods=['GET'])
@token_required
def getLogFile(RN):
    return send_file(FS.GetFolder("LOGS")+'LOG_'+RN+'.txt',as_attachment=True)

if __name__ == '__main__':
    #app.run(host='0.0.0.0', port=5555,debug = True) #for development
    serve(app, host='0.0.0.0', port=5555,threads=12)

