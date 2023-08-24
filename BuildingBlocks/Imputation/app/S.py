#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json,pandas
import time
import C
from threading import Thread
import building_middleware as BB ##importing middleware
import tempfile
import tqdm
import base64
from Postman import postman
from ClientPattern import client_pattern 
from BB_dispatcher import bb_dispatcher 
from ThreadCreator import threadMonitor
import multiprocessing as mp
import gc
import shutil

#solutions
SOLUTIONS_FILE="records.txt"
f_records=  open(SOLUTIONS_FILE,'a+')
f_records.close()

THREADS_LIST= {}


def ClientProcess(metadata,data_acq_time):
    ## ======================================================================= ##
    ## ================================= TIMES =============================== ##
    ## ======================================================================= ##
    TIME_ACQUISITION = data_acq_time
    TIME_SERVICE=0
    TIME_TRANSFORM = 0
    TIME_EXECUTION = 0
    ## ======================================================================= ##
    TIME_SERVICE=time.time()

    # metadata = {"data":data,"DAG":dag,"auth":{"user":token_project}}
    DAG = metadata['DAG'] #dag{}
    data = metadata['data'] #datos {data,type}
    auth = metadata['auth']

    AG=postman(GATEWAYS_LIST,SERVICE_NAME,SERVICE_IP,SERVICE_PORT,NETWORK,TPSHOST,API_GATEWAY=API_GATEWAY,LOGER=LOGER,tokenuser=auth['user'])
    os.chdir(BASE_PATH) #in case of error must be set the base path
    
    service = DAG['service']
    service_name = service
    params = DAG['params']

    children = DAG['childrens'] if 'childrens' in DAG else []
    ENV_VARS = metadata['ENV'] if 'ENV' in metadata else {}

    id_service =DAG['id']
    control_number = DAG['control_number']

    apply_pattern = False
    if 'pattern' in DAG:
        pattern = DAG['pattern']  #{kind:datasplit;datasplit-reduce, variables:[],active:true,workers:5}
        apply_pattern = pattern['active']

    ####### PATCH ###########################################################################
    AG.Set_IdService(id_service)
    AG.Set_RN(control_number)
    AG.start()
    ##########################################################################################
    data = AG.ValidateDataMap(data,auth)

    if 'SAVE_DATA' in params:        
        index_opt = params['SAVE_DATA']
    else:
        index_opt = True # by default
        for key in params:
            if 'SAVE_DATA' in params[key]:
                index_opt = params[key]['SAVE_DATA']
                break

    LOGER.error("====== INDEXING RESULTS : %s" %index_opt)


    if 'actions' in DAG:
        #check if is list
        if type(DAG['actions']) is list:
            actions = DAG['actions']
        else:
            actions=[DAG['actions']] 
            service_name=service_name+"_"+str(DAG['actions'][0])
    else:
        actions = ['REQUEST'] #default exec the first service called REQUEST
        params = {'REQUEST':params}

    LOGER.info("Starting execution process... %s" % id_service)
    LOGER.debug("input path: %s" %data['data'])

    ## ======================================================================= ##
    ## ================================= BBOX ================================ ##
    ## ======================================================================= ##
    TIME_TRANSFORM=time.time()
    if apply_pattern:
        LOGER.info("...### Creating Pattern to ###... %s" % id_service)
        ######### PATTERN EXECUTION #########
        #client_pattern
        CP = client_pattern(control_number,id_service,LOGER=LOGER,POSTMAN=AG,Monitor_Threads=TH_MONITOR)
        result = CP.run_pattern(pattern,data,auth,DAG)
        #index_opt = False #los patrones no indexan datos
    else:
        ############# APP EXECUTION #############
        result = BB.middleware(data,actions,params,LOGER=LOGER,ENV=ENV_VARS,POSTMAN=AG) #{data,type,status,message}
        if 'EXECUTION_TIME' in result:
            TIME_EXECUTION = result['EXECUTION_TIME']
            del result['EXECUTION_TIME']

    del data
    TIME_TRANSFORM=time.time()-TIME_TRANSFORM
    LOGER.info("Finishing execution process... %s" % service_name)
    ## ======================================================================= ##
    ## =========================== ARCHIVE RESULTS =========================== ##
    ## ======================================================================= ##
    LOGER.info("Starting indexing process...%s" % result['data'])
    if index_opt and result['status']!="ERROR": #save results 
        index_time = time.time() #<--- time flag
        label = AG.ArchiveData(result['data'],result['data'].split("/")[-1])
        index_time= time.time() - index_time #<--- time flag
    else:
        label=False
        LOGER.error(result['message'])
        LOGER.info("Skiping index process")
    
    ## ======================================================================= ##
    ## ============================  Abox LOG  =============================== ##
    ## ======================================================================= ##
    with open(SOLUTIONS_FILE,'a+') as f_records:
        # id_service, token_solution ,results path, DAG of childrens
        f_records.write("%s\t%s\t%s\t%s\n" %(id_service,control_number,result['data'],json.dumps(children)))
    ## ======================================================================= ##

    ## ======================================================================= ##
    ## ============================  TERMINATE  ============================== ##
    ## ======================================================================= ##
    ToSend = AG.CreateMessage(control_number,result['message'],result['status'],label=label,type_data=result['type'],index_opt=index_opt,include_hash=True)
    AG.terminate(result['status'],ToSend)
    ## ======================================================================= ##

    ## ======================================================================= ##
    ## ======================= DISPATCH TO CHILDREN  ======================== ##
    ## ======================================================================= ##
    LOGER.info("Sending to children...")
    dispatcher = bb_dispatcher(control_number,id_service,NETWORK,LOGER=LOGER,POSTMAN=AG,Tolerant_errors=Tolerant_errors)
    try:
        for child in children: #list[]
            ##################### HERE 
            if result['status']=="ERROR":
                result['type'] = "error"
                f = tempfile.NamedTemporaryFile(suffix=".error",delete=False)
                f.write("Error".encode())
                fname = f.name
                result['data']=fname
                f.close()
                f = open(fname,"rb")
            else:
                f = open(result['data'],"rb") #open result file to send it to another service

            # send request to the next BB
            dispatcher.Send_to_BB(result,f,auth,child,ENV=ENV_VARS)
    except KeyError as ke:
        LOGER.error("ERROR: we can't find chilfrens children")

    if len(children)<=0:
        LOGER.info("Data sent to all children")
    ## ======================================================================= ##

    #Aqui iba el terminate, pero lo movi arriba para enviar el hash antes de ejecutar los hijos

    #Removing results
    shutil.rmtree(result['data'],ignore_errors=True) 
    del result
    
    TIME_SERVICE=time.time()-TIME_SERVICE
    AG.Set_Time("serv",TIME_SERVICE)
    acq= AG.Get_Times("acq")
    AG.Set_Time("acq",acq+TIME_ACQUISITION)
    AG.Set_Time("trans",TIME_TRANSFORM)
    AG.Set_Time("exec",TIME_EXECUTION)
    AG.ReportTimes()
    AG.join()
    LOGER.info("=========== postman  removed ==============")
    gc.collect()
    return True




#########################################################

BASE_PATH = os.getcwd()
logging.basicConfig(level=logging.INFO)
LOGER = logging.getLogger()
GATEWAYS_LIST =os.getenv("API_GATEWAY").split(",")
NETWORK=os.getenv("NETWORK")
SERVICE_NAME=os.getenv("SERVICE_NAME")
SERVICE_IP=os.getenv("HOSTNAME") 
SERVICE_PORT=os.getenv("SERVICE_PORT") 
TPSHOST = os.getenv("TPS_MANAGER") 





Tolerant_errors=10 #total of errors that can be tolarated
##### TEMP_AG communication handler
TEMP_AG=postman(GATEWAYS_LIST,SERVICE_NAME,SERVICE_IP,SERVICE_PORT,NETWORK,TPSHOST,LOGER=LOGER)

TH_MONITOR = threadMonitor(LOGER=LOGER)
TH_MONITOR.start()


Gtwy = TEMP_AG.Select_gateway()
if Gtwy == 1:
    LOGER.error("BAD GATEWAY")
    time.sleep(2)
    exit(1)
else:
    API_GATEWAY=Gtwy

HEADERSIZE = 4096
port = 80
BUFF_SIZE = 81920*10
SEPARATOR = "<SEPARATOR>"


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((socket.gethostname(), port))
host_name = socket.gethostname() 
host_ip = socket.gethostbyname(host_name) 
LOGER.info("SERVER ON! IP: "+host_ip+" PORT: "+str(port)+"\n\n")
#   init service  #
TEMP_AG.init_service()
serv.listen(Tolerant_errors)

while True:
    conn, addr = serv.accept()
    data_acq_time=time.time()
    LOGER.info("CONECTION FROM: "+str(addr[0])+" PORT: "+str(addr[1])+"\n")

    ### get header ###
    data_to_recv = HEADERSIZE
    reciv_amount = 0
    from_client = []
    while True:
        msg = conn.recv(data_to_recv)
        reciv_amount = len(msg)
        from_client.append(msg)
        if(reciv_amount == data_to_recv):
            msg_size,filesize = b"".join(from_client).decode().split(SEPARATOR) # msg_size <SEPARATOR> filesize
            msglen = int(msg_size)
            filesize = int(filesize)
            break
        else:
            data_to_recv-=reciv_amount

    LOGER.debug("> header recived")

    ### get metadata ###
    data_to_recv = msglen
    reciv_amount = 0
    from_client = []
    while True:
        msg = conn.recv(data_to_recv)
        reciv_amount = len(msg)
        from_client.append(msg)
        if(reciv_amount == data_to_recv):
            metadata= pickle.loads(b"".join(from_client)) #{dag,data}
            break
        else:
            data_to_recv-=reciv_amount

    LOGER.debug("> metadata recived")

    metadata = json.loads(metadata) #loads json {DAG,data}
    file_ext = metadata['data']['type'] 

    INPUT_TEMP_FILE = tempfile.NamedTemporaryFile(delete=False,suffix="."+file_ext) # TEMPORARY FILE TO SAVE DATA
    ### get file ###
    reciv_amount = 0
    LOGER.debug("prepare for recive: %s\n" % file_ext)
    #progress = tqdm.tqdm(range(filesize), f"Receiving data", unit="B", unit_scale=True, unit_divisor=1024)
    while True:
        bytes_read = conn.recv(BUFF_SIZE)
        reciv_amount += len(bytes_read)
        INPUT_TEMP_FILE.write(bytes_read)
        #progress.update(len(bytes_read))
        if reciv_amount>=filesize: 
            break


    inputfile_name =INPUT_TEMP_FILE.name
    INPUT_TEMP_FILE.close() #close temp file (not deleted yet)

    result = json.dumps({'status':'OK'})
    result = pickle.dumps(result)
    result=bytes(f'{len(result):<{HEADERSIZE}}','utf-8')+result
    conn.sendall(result)    

    data_acq_time= time.time()-data_acq_time
    ##########################################################
    if metadata['data']['type'] == "SOLUTION":
        os.remove(inputfile_name)
    else:
        metadata['data']['data'] = inputfile_name
    try:
        thread1 = mp.Process(target = ClientProcess, args = (metadata,data_acq_time) )
        thread1.start()
        TH_MONITOR.AppendThread(thread1)
    except Exception as e:
        LOGER.error(">>>>>>>>>>>>>>>>>>>>< fallo algo al lanzar el thread")

    conn.close()
    
