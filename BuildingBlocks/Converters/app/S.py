#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json,pandas
import requests as api #for APIs request
import time
import C
from threading import Thread
import building_middleware as BB ##importing middleware
import tempfile
import tqdm
import base64
from Postman import postman

#solutions
SOLUTIONS_FILE="records.txt"
f_records=  open(SOLUTIONS_FILE,'a+')
f_records.close()


def ClientProcess(metadata,data_acq_time):
    AG=postman(GATEWAYS_LIST,SERVICE,SERVICE_IP,SERVICE_PORT,NETWORK,TPSHOST,API_GATEWAY=API_GATEWAY)

    os.chdir(BASE_PATH) #in case of error must be set the base path
    DAG = metadata['DAG'] #dag
    data = metadata['data'] #datos {data,type}
    
    service = DAG['service']
    service_name = service
    params = DAG['params']
    childrens = DAG['childrens']
    id_service =DAG['id']
    control_number = DAG['control_number']
    #times
    index_time=0
    execution_time=0
    #validate save data param

    ####### PATCH ###########################################################################
    AG.Set_IdService(id_service)
    AG.Set_RN(control_number)
    AG.start()
    ##########################################################################################

    if 'SAVE_DATA' in params:        
        index_opt = params['SAVE_DATA']
    else:
        for key in params:
            if 'SAVE_DATA' in params[key]:
                index_opt = params[key]['SAVE_DATA']
                break
            else:
                index_opt = False

    if 'actions' in DAG: 
        actions=[DAG['actions']] 
        service_name=service_name+"_"+str(DAG['actions'][0])
    else:
        actions = ['A'] #default exec the first service called A
        params = {'A':params}

    LOGER.error("### INFO: starting execution process... %s" % service_name)
    LOGER.error(data['data'])

    ##### EXECUTION ####
    execution_time=time.time()
    result = BB.middleware(data,actions,params) #{data,type,status,message}
    execution_time=time.time()-execution_time
    LOGER.error("### INFO: Finishing execution process... %s" % service_name)
    del data

    #------------------#
    LOGER.error("### INFO: starting indexing process...%s" % result['data'])
    ###### INDEX #######
    if index_opt and result['status']!="ERROR": #save results 

        temp_filename = result['data']
        file_data = open(temp_filename,"rb")
        result['data']=file_data.read()
        file_data.close()
        result['data'] = base64.b64encode(result['data']).decode('utf-8')


        index_time = time.time() #<--- time flag
        label = AG.IndexData(control_number,id_service,result) #indexing result data into DB

        index_time= time.time() - index_time
        result['data'] = temp_filename
    else:
        label=False
        LOGER.error("### INFO: skiping index process")
    #------------------#
    ########################  save solution's results in diary
    with open(SOLUTIONS_FILE,'a+') as f_records:
        # id_service, control_number,results path, DAG of childrens
        f_records.write("%s\t%s\t%s\t%s\n" %(id_service,control_number,result['data'],json.dumps(childrens)))
    ############################

    ####### WARN #######
    ToSend = {'status':result['status'],"message":result['message'],"label":label,"id":id_service,"type":result['type'], "index":index_opt,"control_number":control_number}
    ToSend['times']={"NAME":service_name,"ACQ":data_acq_time,"EXE":execution_time,"IDX":index_time}
    AG.WarnGateway(ToSend)
    #------------------#

    ##### archive results #####
    if result['status']=="ERROR":
        pass
    else:
        AG.ArchiveData(open(result['data'],"rb"),result['data'].split("/")[-1]) #open result file to send it to another service
    #######################

    AG.terminate()
    LOGER.error("### INFO: sending to childrens...")

###### PATCH
    #OUTPUT_TEMPFILE = tempfile.NamedTemporaryFile(delete=False,suffix="."+result['type'])
    #OUTPUT_TEMPFILE.write(result['data'].encode())
    #output_temp_filename = OUTPUT_TEMPFILE.name
    #OUTPUT_TEMPFILE.close()
    #result['data'] = output_temp_filename
###########
    
    try:

        for child in childrens: #list[]
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
            
            LOGER.error("### INFO: file: %s ..." %result['type'])
            LOGER.error(childrens)
            child['control_number']=control_number ## add control number 
            
            ######## ASK #######
            ToSend = {'service':child['service'],'network':NETWORK}
            res = AG.AskGateway(ToSend)
            #------------------#
            if 'info' in res: #no more nodes
                LOGER.error("NO NODES FOUND")
                data= {'label':'','id':child['id'],'index':'','control_number':control_number,'type':'','status':'ERROR','message': 'no available resources found.'}
                AG.WarnGateway(data)
            else:
                errors_counter=0
                ###### SEND #######
                ip = res['ip'];port = res['port']
                LOGER.error("Children detected... IP:%s PORT: %s " %(ip,port) )
                while(True):
                    #
                    data = C.RestRequest(ip,port,{'data':result,'DAG':child},data_file=f)
                    if data is not None:
                        LOGER.error(">>>>>>> SENT WITH NO ERRORS")
                        #warn successful process
                        warn_success= {'label':'','id':child['id'],'index':'','control_number':control_number,'type':'','status':'INFO','message': child,'parent':id_service}
                        AG.WarnGateway(warn_success)
                        errors_counter=0
                        break;
                    else:
                        errors_counter+=1
                        LOGER.error(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
                        if errors_counter>Tolerant_errors: #we reach the limit
                            ######## ASK AGAIN #######
                            ToSend = {'service':child['service'],'network':NETWORK,'update':{'id':res['id'],'status':'DOWN',"type":res['type']}} #update status of falied node
                            res = AG.AskGateway(ToSend)
                            #------------------#
                            errors_counter=0 #reset counter 
                            if 'info' in res: #no more nodes
                                data= {'label':'','id':child['id'],'index':'','control_number':control_number,'type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
                                AG.WarnGateway(data)
                                break
                            ip = res['ip'];port = res['port']
                            LOGER.error("TRYING A NEW NODE... IP:%s PORT: %s " %(ip,port) )


    except KeyError as ke:
        LOGER.error("No more childrens")

    if len(childrens)<=0:
        LOGER.error("Data sent to all childrens")

    #here it will be the rollback function
    del result




#########################################################

BASE_PATH = os.getcwd()
LOGER = logging.getLogger()
GATEWAYS_LIST =os.getenv("API_GATEWAY").split(",")
NETWORK=os.getenv("NETWORK")
SERVICE=os.getenv("SERVICE")
SERVICE_IP=os.getenv("SERVICE_IP") 
SERVICE_PORT=os.getenv("SERVICE_PORT") 
TPSHOST = os.getenv("TPS_MANAGER") 

Tolerant_errors=10 #total of errors that can be tolarated

##### TEMP_AG communication handler
TEMP_AG=postman(GATEWAYS_LIST,SERVICE,SERVICE_IP,SERVICE_PORT,NETWORK,TPSHOST)

Gtwy = TEMP_AG.Select_gateway()
if Gtwy == 1:
    LOGER.error("BAD GATEWAY")
    exit(1)
else:
    API_GATEWAY=Gtwy

HEADERSIZE = 4096
port = 80
BUFF_SIZE = 81920
SEPARATOR = "<SEPARATOR>"


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((socket.gethostname(), port))
host_name = socket.gethostname() 
host_ip = socket.gethostbyname(host_name) 
LOGER.error("SERVER ON! IP: "+host_ip+" PORT: "+str(port)+"\n\n")
#   init service  #
TEMP_AG.init_service()
serv.listen(Tolerant_errors)

while True:
    conn, addr = serv.accept()
    data_acq_time=time.time()
    LOGER.error("CONECTION FROM: "+str(addr[0])+" PORT: "+str(addr[1])+"\n")

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

    LOGER.error("> header recived")

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

    LOGER.error("> metadata recived")

    file_ext =json.loads(metadata)['data']['type'] 

    INPUT_TEMP_FILE = tempfile.NamedTemporaryFile(delete=False,suffix="."+file_ext) # TEMPORARY FILE TO SAVE DATA
    ### get file ###
    reciv_amount = 0
    LOGER.error("prepare for recive: %s\n" % file_ext)
    progress = tqdm.tqdm(range(filesize), f"Receiving data", unit="B", unit_scale=True, unit_divisor=1024)
    while True:
        bytes_read = conn.recv(BUFF_SIZE)
        reciv_amount += len(bytes_read)
        INPUT_TEMP_FILE.write(bytes_read)
        progress.update(len(bytes_read))

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
    metadata = json.loads(metadata) #loads json {DAG,data}
    metadata['data']['data'] = inputfile_name
    thread1 = Thread(target = ClientProcess, args = (metadata,data_acq_time) )
    thread1.start()

    
