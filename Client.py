import json
import requests
import sys
import time


ip = sys.argv[1]
path_inst = sys.argv[2]
path_data = sys.argv[3]

data="NA"
data_type="json"

if path_data== "" or path_data=="NA":
    pass
else:
    #read data
    with open(path_data,"rb") as f:
        data= f.read()

#read instructions
with open(path_inst,"r") as f:
    data_json= f.read()
    inst = json.loads(data_json)["DAG"]

    #print(inst["dataobject"]['children'])


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
print("Executing...\n")

ToSend = {"data":json.dumps({"data":data,"type":data_type}),
            "DAG":json.dumps(inst)
}

r = requests.post('http://'+ip+'/executeDAG', json=ToSend)

print(json.loads(r.text))
RN = json.loads(r.text)['RN']

print("\n Mesh is processing request in background")
#monitoring
i=0
to_download = []
while True:
    r = requests.post('http://'+ip+'/monitor/'+str(RN))
    response = json.loads(r.text)

    if response['status'] =="OK":
        print(response)
        if response['index']==True:
            to_download.append(response)
        i+=1
    if i >=count:
        print("solution complete")
        break
    time.sleep(1)


print("\n \tdownload data using wget commands:")
for x in to_download:
    url = "wget http://%s/getfile/%s/%s" %(ip,RN,x['task'])
    print(url)

