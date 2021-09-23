import json,sys

name_jsonfile = sys.argv[1]

with open(name_jsonfile+".json") as json_file:
    data= json.load(json_file)
    
print(data)

with open(name_jsonfile+"pretty.json","w") as f:
    f.write(json.dumps(data,indent=2))