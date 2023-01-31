#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json
import requests as api #for APIs request
import time
import C
from threading import Thread


def init_service():
    try:
        if SERVICE_IP is not None and SERVICE_PORT is not None:
            ToSend=json.dumps({"SERVICE":"gateway","IP":SERVICE_IP,"PORT":int(SERVICE_PORT),"NETWORK":NETWORK})
            url = 'http://%s/ADD' % API_GATEWAY
            headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
            res =api.post(url, data=ToSend,headers=headers).json()
            LOGER.error("INIT")
        else:
            LOGER.error("NOT ENOUGH INFO TO INIT")
    except Exception as e:
        LOGER.error("ERROR: %s" % e)
        LOGER.error("BAD PARAMETERS")
        exit(1)



def WarnGateway(ToSend):
    global API_GATEWAY
    ToSend=json.dumps(ToSend)

    url = 'http://%s/WARN' % API_GATEWAY
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    return api.post(url, data=ToSend,headers=headers)

def ReportToGateway(ToSend):
    global API_GATEWAY
    ToSend=json.dumps(ToSend)
    url = 'http://%s/TIMES' % API_GATEWAY
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    return api.post(url, data=ToSend,headers=headers)

def ClientProcess(data,data_acq_time):
    os.chdir(BASE_PATH) #in case of error must be set the base path
    data = json.loads(data)
    DAG = data['DAG'] #dag
    result = data['data'] #datos {data,type}
    del data
    exec_time = time.time()
    service = DAG['service']
    service_name = service
    params = DAG['params']
    childrens = DAG['childrens']
    id_service =DAG['id']
    control_number = DAG['control_number']

    LOGER.error("### INFO: Redirecting to service...")

    try:
        ######## ASK #######
        ToSend = {'service':service,'network':NETWORK,'force':True}
        ToSend=json.dumps(ToSend)
        url = 'http://%s/ASK' % API_GATEWAY
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
        res = api.post(url, data=ToSend,headers=headers).json()
        #------------------#
        errors_counter=0
        ###### SEND #######
        ip = res['ip'];port = res['port']
        LOGER.error("Node detected... IP:%s PORT: %s " %(ip,port) )
        while(True):
            #
            data = C.RestRequest(ip,port,{'data':result,'DAG':DAG})
            if data is not None:
                LOGER.error(">>>>>>> SENT WITH NO ERRORS")
                errors_counter=0
                break;
            else:
                errors_counter+=1
                LOGER.error(">>>>>>> NODE FAILED... TRYING AGAIN..%s" % errors_counter)
                if errors_counter>Tolerant_errors: #we reach the limit
                    ######## ASK AGAIN #######
                    ToSend = {'service':service,'network':NETWORK,"force":True,'update':{'id':res['id'],'status':'DOWN'}} #update status of falied node
                    ToSend=json.dumps(ToSend)
                    url = 'http://%s/ASK' % API_GATEWAY
                    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
                    res = api.post(url, data=ToSend,headers=headers).json()
                    errors_counter=0 #reset counter 
                    #------------------#
                    if 'info' in res: #no more nodes
                        data= {'label':'','id':DAG['id'],'index':'','control_number':control_number,'type':'','status':'ERROR','message': 'no available resources found: %s attempts.' % str(errors_counter)}
                        WarnGateway(data)
                        break
                    ip = res['ip'];port = res['port']
                    LOGER.error("TRYING A NEW NODE... IP:%s PORT: %s " %(ip,port) )


            #------------------#


    except KeyError as ke:
        LOGER.error("No more nodes")

    del result
    exec_time=time.time()-exec_time
    ToSend={"times":{"NAME":"GATEWAY_"+NETWORK,"ACQ":data_acq_time,"EXE":exec_time},"control_number":control_number}
    ReportToGateway(ToSend)


#########################################################

BASE_PATH = os.getcwd()
LOGER = logging.getLogger()
#API_GATEWAY="coordinator:5555"
API_GATEWAY=os.getenv("API_GATEWAY") 
NETWORK=os.getenv("NETWORK") 
SERVICE_IP=os.getenv("SERVICE_IP") 
SERVICE_PORT=os.getenv("SERVICE_PORT") 
Tolerant_errors=10 #total of errors that can be tolarated


HEADERSIZE = 4096
port = 80
BUFF_SIZE = 81920
serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((socket.gethostname(), port))
host_name = socket.gethostname() 
host_ip = socket.gethostbyname(host_name) 
LOGER.error("SERVIDOR ENCENDIDO! IP: "+host_ip+" PORT: "+str(port)+"\n\n")
init_service()
serv.listen(10)

while True:
    conn, addr = serv.accept()
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

    
