import sys,os,ast
import pandas as pd
from threading import Thread
from flask import Flask,request,jsonify,send_file
import json
from time import sleep
import C
import logging #logger
from base64 import b64encode,b64decode
import io
import tempfile
import shutil

# local imports
from functions import *
from TwoChoices import loadbalancer
from TPS.Builder import Builder #TPS API BUILDER
from Proposer import Paxos


########## GLOBAL VARIABLES ##########
with open('coordinator_structure.json') as json_file:
    dictionary = json.load(json_file) #read all configurations for services

logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()
WORKSPACENAME = "SERVICEMESH" #equivalente a catalogo en skycds, es decir, una solucion o un DAG
TPSHOST ="http://tps_manager:5000"
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

INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data

#select load blaancer
LOAD_B = loadbalancer(dictionary)
Tolerant_errors=25 #total of errors that can be tolarated
ACCEPTORS_LIST= dictionary['paxos']["accepters"]
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
            tmp = os.listdir(path)
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


def GetWorkspacePath(tokenuser,workspace):
    #se creara el cataloog de fuentes de datos si es que no existe
    createFolderIfNotExist("%s%s" %(SPL_FOLDER,tokenuser))
    createFolderIfNotExist("%s%s/%s" %(SPL_FOLDER,tokenuser,workspace)) #create folders of user and workspace
    return "%s%s/%s/" %(SPL_FOLDER,tokenuser,workspace)


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
    
#service to execute applications
def execute_service(service,metadata):
    f = open(metadata['data']['data'],"rb")

    LOGER.info("Coordinator is executing...%s"% service)
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
            LOGER.info(">>>>>>> SENT WITH NO ERRORS")
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
    LOGER.info("finishing execution...%s"% service)


app = Flask(__name__)

#root service
@app.route('/')
def prueba():
    return {"status":"OK","message":"xel is online."}

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
        LOGER.info("REGISTRED %s, ip:%s port: %s" % (service,service_ip,service_port))
    else:
        LOGER.info("ALREADY REGISTRED %s, ip:%s port: %s " % (service,service_ip,service_port))

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
            LOGER.info("REDIRECTING TO INTERNAL GATEWAY..")
            #

            iag = LOAD_B.SelectGateway(res['network'])
            if iag is not None:
                res = iag
                res['type'] = "gateway"
                LOGER.debug("GATEWAY: %s, NETWORK: %s" %(res['ip'],res['network']))
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
    for branch in new_dag:
        branch['control_number'] = RN
        if branch['id'] in task_list:

            parent = task_list[branch['id']]['parent']
            path_bk_data = "%s%s/%s" %(BKP_FOLDER,RN,parent)
            tmp = os.listdir(path_bk_data)
            path_bk_data +="/"+tmp[0]
            LOGER.info("recovering data from %s ..." % path_bk_data)

            data_format ={"data":path_bk_data,"type":path_bk_data.split(".")[-1]}
            metadata = {"data":data,"DAG":branch}
            service = branch['service'] #name of the service to send the instructions
            thread1 = Thread(target = execute_service, args = (service,metadata))
            thread1.start()
        else:
            metadata = {"data":data,"DAG":branch}
            service = branch['service']
            thread1 = Thread(target = execute_service, args = (service,metadata) )
            thread1.start()
            sleep(.5)

    return json.dumps({"status":"OK",'token_solution':RN,"DAG":DAG})


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

    if 'DAG' in value: #el nodo fallo al estar procesando datos... se van a recuperar
        dag = value['DAG']
        parent = value['parent']

        path_bk_data = "%s%s/%s" %(BKP_FOLDER,RN,parent)
        tmp = os.listdir(path_bk_data)
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
@app.route('/RetrieveSolution', methods=['POST'])
def retrieve_sol_from_DB():
    params = request.get_json(force=True)
    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
    token_solution = params['token_solution']
     ######## paxos ##########
    paxos_response = PROPOSER.Retrieve(token_solution,auth) # consult request in paxos distributed memory
    #########################
    return {"status":paxos_response['status'],"info":paxos_response['value']}    

@app.route('/StoreSolution', methods=['POST'])
def store_sol_in_DB():
    params = request.get_json(force=True)
    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}
    metadata = params['metadata'] #metadata of the solution {name,desc,frontend}
    DAG = params['DAG'] #it have the parameters, the sub dag ,and the secuence of execution (its a json).
    #token_solution = params['token_solution']
    token_solution = CreateSolutionID(params)
    
    ######## paxos ##########
    paxos_response = PROPOSER.Store(token_solution,DAG,metadata,auth) # consult request in paxos distributed memory
    #########################
    return {"status":paxos_response['status'], "message":paxos_response['value'],"info":{"token_solution":token_solution}}

@app.route('/ListSolutions', methods=['POST'])
def List_solutions_user():
    params = request.get_json(force=True)

    auth = params['auth'] #params wich define the enviroment  {user:,workspace:}

    ######## paxos ##########
    paxos_response = PROPOSER.list_solutions(auth) # consult request in paxos distributed memory
    #########################
    return {"status":"OK", "info":paxos_response['value']}


@app.route('/ArchiveData/<RN>/<task>', methods = ['POST'])
def upload_file(RN,task):
    tmp_f = createFolderIfNotExist("%s/" % RN,wd=BKP_FOLDER)
    path_to_archive= createFolderIfNotExist("%s/" % task,wd=tmp_f)
    f = request.files['file']
    filename = f.filename
    f.save(os.path.join(path_to_archive, filename))
    return json.dumps({"status":"OK", "message":"OK"})



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
    def verify_extentions(data_path,ext,response,filename):
        valid = False #flag to mark a valid file

        if ext=="zip":
            valid=True
            dirpath,list_of_files=zip_extraction(data_path)
            for fname in list_of_files:
                fext= fname.split(".")[1]
                response,file_validation = verify_extentions(dirpath+"/"+fname,fext,response,fname) #recursive
                response['info']['list_of_files'].append(fname)
            # must delete the temp folder
            shutil.rmtree(dirpath)

        elif ext=="csv":  #describe csv
            dataset= pd.read_csv(data_path)
            response['info']['files_info'][filename] = DatasetDescription(dataset)
            valid=True
        elif ext=="json":
            dataset = pd.read_json(data_path)
            response['info']['files_info'][filename] = DatasetDescription(dataset)
            valid=True

        return response,valid 


    params = request.get_json(force=True)
    
    data_path,name,ext= GetDataPath(params) #Inspect the type of dataset request and get returns the path for the data
    LOGER.info(data_path)
    filename = "%s.%s" %(name,ext)

    response={"status":"OK","message":"","info":{"parent_filename":filename,"list_of_files":[],"files_info":{}}}

    response,file_validation=verify_extentions(data_path,ext,response,filename)
    if file_validation:
        pass
    else:
        response['status']="ERROR"
        response['message']="Datafile can't be described. Try with the followinf file extentions:csv,json,zip or tar."

    return response




@app.route('/getlog/<RN>', methods=['GET'])
def getLogFile(RN):
    return send_file(logs_folder+'log_'+RN+'.txt',as_attachment=True)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5555,debug = True)
