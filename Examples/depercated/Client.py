import json
import requests as api
import sys
import time
import time, sys
from threading import Thread

def waiting(lenstr=20, zzz=0.5, dispstr='Mesh is now processing request in background'):
    dots   = '.' * lenstr
    spaces = ' ' * lenstr
    print(dispstr.center(lenstr, '*'))
    while True:
        for i in range(lenstr):
            time.sleep(zzz)
            outstr = dots[:i] + spaces[i:]
            sys.stdout.write('\b' * lenstr + outstr)
            sys.stdout.flush()

        for i in range(lenstr, 0, -1):
            time.sleep(zzz)
            outstr = dots[:i] + spaces[i:]
            sys.stdout.write('\b' * lenstr + outstr)   
            sys.stdout.flush()  

MESH_USER="Geoportal"
MESH_WORKSPACE="Default"

IP = sys.argv[1] #ip for the xel gateway 
if IP=="":
    IP="localhost:25000" #ip by default

path_inst = sys.argv[2] #path of the file with the instructions /some examples found in ./Examples/Solutions
path_data = sys.argv[3] #path with the input data, some examples do not need this 

data_map={'data':'','type':'DUMMY'} #map to indicate where is input data.

# DUMMY: data input is not needed
# LAKE: data input is taken from the mesh's lake




### STEP 1 | UPLOAD DATA ###
if path_data== "" or path_data=="NA":
    pass
else:
    #read data
    namefile= path_data.split("/")[-1]
    name,ext= namefile.split(".")
    with open(path_data,"rb") as f:
        values={"workspace":MESH_WORKSPACE,"user":MESH_USER}
        url = 'http://%s/UploadDataset'% (IP)
        res = api.post(url, files={"file":(namefile,f)},data=values).json()
        if res['status']=="OK":
            print("data uploaded sucessfully")
            data_map= {'data':{'token_user':MESH_USER,'catalog':MESH_WORKSPACE,'filename':namefile},'type':'LAKE'}
        else:
            print("ERROR: data couldn't be uploaded")
            exit()

##################################
### STEP 2 | SEND THE INSTRUCTIONS ###

#read instructions
with open(path_inst,"r") as f:
    data_json= f.read()
    inst = json.loads(data_json)["DAG"]

#count childrens
def count_childrens(arr):
    count = 0
    if len(arr)>0:
        for a in arr:
            count += count_childrens(a['childrens'])
        return 1+ count
    else:
        return 1


count= count_childrens(inst)-1
print("> Sending dag...\n")


#dag must be sent as string
ToSend = {"data_map":data_map,
            "DAG":json.dumps(inst),
            'auth':{'user':MESH_USER,'workspace':MESH_WORKSPACE}}

r = api.post('http://'+IP+'/executeDAG', json=ToSend)

print(json.loads(r.text))
RN = json.loads(r.text)['token_solution']

print("\n")
thread1 = Thread(target = waiting,daemon=True).start()

### STEP 3 | MONITORING ###
i=0
to_download = []
while True:
    r = api.post('http://'+IP+'/monitor/'+str(RN))
    response = json.loads(r.text)

    if response['status'] =="OK":
        print("\n")
        print(response)
        if response['index']==True:
            to_download.append(response)
        i+=1
    if i >=count:
        print("> SOLUTION COMPLETE")
        break
    time.sleep(1)

### STEP 4 | RESULTS ###

print("\n \t > download the results using following URL's")
for x in to_download:
    url = "http://%s/getfile/%s/%s" %(IP,RN,x['task'])
    print(url)

"""
def download_url(url, directory):

    response = requests.get(url, stream=True)
    if response.status != 200:
        raise ValueError('Failed to download')

    params = cgi.parse_header(
        response.headers.get('Content-Disposition', ''))[-1]
    if 'filename' not in params:
        raise ValueError('Could not find a filename')

    filename = os.path.basename(params['filename'])
    abs_path = os.path.join(directory, filename)
    with open(abs_path, 'wb') as target:
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, target)

    return filename
"""