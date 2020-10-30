#import building_middleware as BB ##importing middleware
import logging #logger
import socket,os,sys,pickle,json,pandas


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
    import building_middleware as BB ##importing middleware
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











'''import sys,os,pandas,ast
from threading import Thread
from flask import request, url_for
from flask import Flask, request,jsonify,Response
import building_middleware as BB ##importing middleware
import json

BASE_PATH = os.getcwd()


app = Flask(__name__)
#root service
@app.route('/')
def prueba():
    return "Service Mersh"

#service to execute applications
@app.route('/execute', methods=['POST'])
def execute_service():
    os.chdir(BASE_PATH) #in case of error must be set the base path
    params = request.get_json()
    data = params['data'] #data to be transform
    actions = params['actions'] #dag
    service_params = params['params'] #parameters for the service
    result = BB.middleware(data,actions,service_params) #returns the result as json
    return result

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=80,debug = True)

'''