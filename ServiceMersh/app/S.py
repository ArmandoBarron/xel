#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json,pandas

from TPS.Builder import Builder #TPS API BUILDER
INDEXER=Builder(WORKSPACENAME,TPS_manager_host=TPSHOST) #api for index data


def ReciveDataFromClient(conn,BUFF_SIZE,HEADERSIZE):
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
    return data

BASE_PATH = os.getcwd()
LOGER = logging.getLogger()


HEADERSIZE = 4096
port = 80
BUFF_SIZE = 81920


serv = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serv.bind((socket.gethostname(), port))
host_name = socket.gethostname() 
host_ip = socket.gethostbyname(host_name) 
LOGER.error("SERVIDOR ENCENDIDO! IP: "+host_ip+" PORT: "+str(port)+"\n\n")
serv.listen(5)

while True:
    conn, addr = serv.accept()
    LOGER.error("CONECTION FROM: "+str(addr[0])+" PORT: "+str(addr[1])+"\n")
    
    data = ReciveDataFromClient(conn,BUFF_SIZE,HEADERSIZE)
    data = json.loads(data)
    order = data['order']

    if order == "INDEX":
    elif order == "WARN":
    elif order == "ASK":
    else:
        pass

     
    os.chdir(BASE_PATH) #in case of error must be set the base path
    params = json.loads(data)
    data_a = params['data']
    actions = params['actions'] #dag
    service_params = params['params'] #parameters for the service
    result = BB.middleware(data_a,actions,service_params) #returns the result as json
    result = json.dumps(result)
    LOGER.error("PREPARANDO ENVIO DE DATOS \n")

    result = pickle.dumps(result)
    result=bytes(f'{len(result):<{HEADERSIZE}}','utf-8')+result
    LOGER.error("no se envian los datos \n")

    conn.sendall(result)    
    
    LOGER.error("o si \n")
    del data
    del result








