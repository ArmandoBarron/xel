import socket
import sys
import pickle
import json
import requests as api #for APIs request
import logging #logger


LOGER = logging.getLogger()

def RestRequest(ip,port,message):
  HEADERSIZE = 4096
  BUFF_SIZE = 81920

  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    client.connect((ip, port))
    message=json.dumps(message)
    msg = pickle.dumps(message)
    msg=bytes(f'{len(msg):<{HEADERSIZE}}','utf-8')+msg
    client.sendall(msg)
    from_server = []
    newMessage = True
    reciv_amount=0
    while True:
      #LOGER.error("esperando respuesta..")
      reply = client.recv(BUFF_SIZE)
      reciv_amount += len(reply)
      #LOGER.error(len(reply))
      if(newMessage):
        msglen = int(reply[:HEADERSIZE])
        LOGER.error(msglen)
        newMessage = False
      
      from_server.append(reply)
      
      if(msglen<=reciv_amount-HEADERSIZE):
        LOGER.error("respuesta obtenida..")
        from_server = b"".join(from_server)
        LOGER.error(len(from_server))
        ans = pickle.loads(from_server[HEADERSIZE:])
        client.close()
        return json.loads(ans)
        #newMessage = True
        #from_server = ''

  except socket.error as exc:
    client.close()
    return None


        
        
        
'''
LOGER.error("LLEGO AL C")
LOGER.error(message)
url = 'http://%s:%s/execute' %(ip,port) #calling the bb
LOGER.error(url)
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
result = api.post(url, data=json.dumps(message),headers=headers)
LOGER.error("1")
LOGER.error(result)
RES = result.json()
LOGER.error("2")
#LOGER.error(RES)
return RES
'''
