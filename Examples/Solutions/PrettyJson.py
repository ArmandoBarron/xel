import json

name_jsonfile = "Classification_control_test"
with open(name_jsonfile+".json") as json_file:
    data= json.load(json_file)

with open(name_jsonfile+"pretty.json","w") as f:
    f.write(json.dumps(data,indent=2))