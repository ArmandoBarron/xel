import socket
import sys
import pickle
import json
import requests as api #for APIs request
import logging #logger
import tempfile
import os
import time

LOGER = logging.getLogger()

def RestRequest(ip,port,metadata,data_file=tempfile.NamedTemporaryFile()):
  HEADERSIZE = 4096
  BUFF_SIZE = 81920 * 10
  SEPARATOR = "<SEPARATOR>"
  filesize= os.stat(data_file.name).st_size
  client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  try:
    client.connect((ip, port))
    msg = pickle.dumps(json.dumps(metadata))
    header_message = f"{len(msg)}{SEPARATOR}{filesize}"
    msg=bytes(f'{header_message:<{HEADERSIZE}}','utf-8')+msg #send metadata
    client.sendall(msg) #metadata sent. msg_size <SEPARATOR> filesize < HEADERSIZE... + Hedearsize> metadata < filesize 

    #send file
    LOGER.error("FILESIZE: %s \n" % filesize)
    while True:
        # read the bytes from the file
        bytes_read = data_file.read(BUFF_SIZE)
        if not bytes_read:
            # file transmitting is done
            LOGER.error("NO MORE BYTES TO SEND: %s" % len(bytes_read))
            break
        # we use sendall to assure transimission in 
        # busy networks
        client.sendall(bytes_read)
        # update the progress bar
  
    data_file.close()
    from_server = []
    newMessage = True
    reciv_amount=0
    while True:
      LOGER.error("waiting...")
      reply = client.recv(HEADERSIZE)
      reciv_amount += len(reply)
      if(newMessage):
        msglen = int(reply[:HEADERSIZE])
        newMessage = False
      
      from_server.append(reply)
      
      if(msglen<=reciv_amount-HEADERSIZE):
        from_server = b"".join(from_server)
        ans = pickle.loads(from_server[HEADERSIZE:])
        client.close()
        return json.loads(ans)


  except socket.error as exc:
    client.close()
    return None
