import json
import requests as api #for APIs request
import shutil
import os
import tempfile
import pandas as pd
import cgi

API_GATEWAY = "localhost:25000"

task = "c1-DST"
token_solution = "81cd026e7b7b3f1594d29b7e84f72e35ce730b093fd99c07cadc9ab0661ec2f6"
MESH_USER="geoportal"
MESH_WORKSPACE = "Default"
ToSend = {'data':{},'type':""}
ToSend["data"]["token_user"]=MESH_USER
ToSend["data"]["token_solution"]=token_solution 
ToSend["data"]["task"]=task
ToSend["data"]["catalog"]=MESH_WORKSPACE
ToSend["type"] ="SOLUTION"



ToSend=json.dumps(ToSend)
url = 'http://%s/getfile' % API_GATEWAY
headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
response = api.post(url, data=ToSend,headers=headers,stream=True)
print(response.headers)

params = cgi.parse_header(
        response.headers.get('Content-Disposition', ''))[-1]
print(params['filename'])


"""
file_group = tempfile.NamedTemporaryFile(delete=False,suffix=".csv") # TEMPORARY FILE TO SAVE DATA
fname = file_group.name
file_group.close()
with open(fname, 'wb') as target:
    response.raw.decode_content = True
    shutil.copyfileobj(response.raw, target)

print("se guardo, ahora hay que abrirlo")
df = pd.read_csv(fname)
print(df)

"""
