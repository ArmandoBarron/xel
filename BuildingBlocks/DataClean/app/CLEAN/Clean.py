import sys
import os
import json

import pandas as pd
import numpy as np
from scipy import stats

def validate_int(val,defult_value=0):
    if val != "" and val!="-":
        return int(val)
    else:
        return defult_value

def validate_string(val,defult_value=""):
    if val != "" and val!="-":
        return val
    else:
        return defult_value

def validate_numeric(val):
    if val.lstrip('-').isdigit(): # es un numero entero
        return int(val)
    else:
        try: #verificar si es float
            a =float(val)
            return a
        except ValueError: # no es, entonces no es un numero
            return val


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns
list_values= sys.argv[4].split(",") #
replace_with = validate_string(sys.argv[5],defult_value=np.nan) # NaN or other value

print(replace_with is not np.nan)
if replace_with is not np.nan:
    replace_with = validate_numeric(replace_with) # para validar si puede ser un int

DF_data = pd.read_csv(data_path)

for col in columns:
    for v in list_values:
        v = validate_numeric(v) 
        #print(v)
        #print(type(v))
        DF_data[col] = DF_data[col].replace(v,replace_with)

DF_data.to_csv(output_path,index=False)