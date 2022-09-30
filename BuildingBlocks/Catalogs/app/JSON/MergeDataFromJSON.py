import pandas as pd
import numpy as np
import sys
import os 
import json
ACTUAL_PATH = os.path.dirname(os.path.abspath(__file__)) + "/"

inputpath=sys.argv[1]
outputpath=sys.argv[2]

JSON_DATA =sys.argv[3]
COLUMN_KEY = sys.argv[4]

df_data = pd.read_csv(inputpath)

print(JSON_DATA)

json_data =json.loads(JSON_DATA)


dicts=df_data[COLUMN_KEY].map(json_data)

print(dicts)

dict_columns = dict()    
for d in dicts:
    for key in d.keys():
        if key not in dict_columns:
            dict_columns[key] =[]
        dict_columns[key].append(d[key]) 


## pasar columnas al dataset original

for key in dict_columns.keys():
    df_data[key]=dict_columns[key]



df_data.to_csv(outputpath,index=False)


