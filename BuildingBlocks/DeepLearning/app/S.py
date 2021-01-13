#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json,pandas
from TPS.Builder import Builder #TPS API BUILDER
import requests as api #for APIs request
import time
import C
from threading import Thread

def IndexData(RN,id_service,data):
    WORKSPACENAME = "SERVICEMESH"
    #TPSHOST ="http://tps_manager:5000"
    TPSHOST = os.getenv("TPS_MANAGER") 

    INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data
    try:
        INDEXER.TPSapi.format_single_query("notImportant")
    except AttributeError:
        INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data


    data_label = "%s_%s" % (RN,id_service) #this is the name of the document (mongo document)
    query = INDEXER.TPSapi.format_single_query("notImportant") #not important line. Well yes but actually no.
    res = INDEXER.TPSapi.TPS(query,"indexdata",workload=data,label=data_label) #this service (getdata) let me send json data and save it into a mongo DB
    return data_label

def WarnGateway(ToSend):
    global API_GATEWAY
    ToSend=json.dumps(ToSend)

    url = 'http://%s/WARN' % API_GATEWAY
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    return api.post(url, data=ToSend,headers=headers)

def ClientProcess(data,data_acq_time):
    os.chdir(BASE_PATH) #in case of error must be set the base path
    data = json.loads(data)
    DAG = data['DAG'] #dag
    data = data['data'] #datos {data,type}

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
    ##### EXECUTION ####
    execution_time=time.time()
    result = BB.middleware(data,actions,params) #{data,type,status,message}
    execution_time=time.time()-execution_time
    LOGER.error("### INFO: Finishing execution process... %s" % service_name)

    del data

    #------------------#
    LOGER.error("### INFO: starting indexing process...")

    ###### INDEX #######
    if index_opt: #save results 
        index_time = time.time() #<--- time flag
        label = IndexData(control_number,id_service,result) #indexing result data into DB
        index_time= time.time() - index_time

    else:
        label=False
        LOGER.error("### INFO: skiping index process")
    #------------------#

    ####### WARN #######
    #ToSend = {'data':json.dumps({'data':data,'type':'zip'}),'DAG':DAG}
    ToSend = {'status':result['status'],"message":result['message'],"label":label,"id":id_service,"type":result['type'], "index":index_opt,"control_number":control_number}
    ToSend['times']={"NAME":service_name,"ACQ":data_acq_time,"EXE":execution_time,"IDX":index_time}
    WarnGateway(ToSend)
    #------------------#

    LOGER.error("### INFO: sending to childrens...")

    try:
        for child in childrens: #list[]
            errors_counter=0
            child['control_number']=control_number ## add control number 
            while(True):
                 ######## ASK #######
                ToSend = {'service':child['service']}
                ToSend=json.dumps(ToSend)
                url = 'http://%s/ASK' % API_GATEWAY
                headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                res = api.post(url, data=ToSend,headers=headers).json()
                #------------------#


                ####### SEND #######
                ip = res['ip']
                port = res['port']
                LOGER.error(res['workload'])
                LOGER.error("Children detected... IP:%s PORT: %s " %(ip,port) )
                data = C.RestRequest(ip,port,{'data':result,'DAG':child})
                LOGER.error("INFO SENT TO CHILDREN")
                if data is not None:
                    LOGER.error(">>>>>>> SENT WITH NO ERRORS")
                    errors_counter=0
                    break;
                else:
                    errors_counter+=1
                    LOGER.error(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
                    if errors_counter>Tolerant_errors: #we reach the limit
                        data= {'label':'','id':id_service,'index':'','control_number':control_number,'type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
                        WarnGateway(data)
                        break

                #------------------#


    except KeyError as ke:
        LOGER.error("No more childrens")

    if len(childrens)<=0:
        LOGER.error("No more childrens")

    del result




#########################################################

BASE_PATH = os.getcwd()
LOGER = logging.getLogger()
#API_GATEWAY="coordinator:5555"
API_GATEWAY=os.getenv("API_GATEWAY") 
Tolerant_errors=25 #total of errors that can be tolarated


HEADERSIZE = 4096
port = 80
BUFF_SIZE = 81920
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((socket.gethostname(), port))
host_name = socket.gethostname() 
host_ip = socket.gethostbyname(host_name) 
LOGER.error("SERVIDOR ENCENDIDO! IP: "+host_ip+" PORT: "+str(port)+"\n\n")
serv.listen(10)

while True:
    conn, addr = serv.accept()
    import building_middleware as BB ##importing middleware
    data_acq_time=time.time()
    LOGER.error("CONECTION FROM: "+str(addr[0])+" PORT: "+str(addr[1])+"\n")
    
    from_client = []
    newMessage = True
    reciv_amount=0

    while True:
        data = conn.recv(BUFF_SIZE)
        reciv_amount += len(data)

        if(newMessage):
            msglen = int(data[:HEADERSIZE])
            LOGER.error(msglen)
            newMessage = False
            
        from_client.append(data)
        
        if(msglen<=reciv_amount-HEADERSIZE):
            from_client = b"".join(from_client)
            data = pickle.loads(from_client[HEADERSIZE:])
            newMessage = True
            from_client = ''
            break
    
    result = json.dumps({'status':'OK'})
    result = pickle.dumps(result)
    result=bytes(f'{len(result):<{HEADERSIZE}}','utf-8')+result
    conn.sendall(result)    

    data_acq_time= time.time()-data_acq_time
    ##########################################################
    thread1 = Thread(target = ClientProcess, args = (data,data_acq_time) )
    thread1.start()

    
