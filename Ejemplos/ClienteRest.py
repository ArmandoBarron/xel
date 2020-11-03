import os,json
import requests as api #for APIs request
import pandas as pd
from base64 import b64decode


DAG= json.load(open("ejemploGLOVE.json","r")) #DAG

#with open('ejemploGLOVE.json', 'w') as outfile:
#    json.dump(DAG['dataobject']['children'], outfile, indent=4)
#exit()


ToSend = {'data':{"data":"","type":""},'DAG':DAG} #no actions, so it will taken the default application A

ToSend=json.dumps(ToSend)

url = 'http://localhost:25000/executeDAG'
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
result = api.post(url, data=ToSend,headers=headers)
RES = result.json()


RN = RES['RN'] #get RN to monitoring

Notask = 3
while True:
    if Notask <=0: break
    url = 'http://localhost:25000/monitor/%s' % (RN)
    headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
    result = api.post(url,headers=headers)
    RES = result.json()
    if RES['status'] == "OK":
        print(RES['data'])
        print("DATA FOUNDED")
        print(RES['task'])
        Notask-=1
    else:
        print("nothing yet")








