import sys
import os
import json

import pandas as pd
import numpy as np
from scipy import stats

def validate_int(val,default_value=0):
    if val != "" and val!="-":
        return int(val)
    else:
        return default_value

def validate_string(val,default_value=""):
    if val != "" and val!="-":
        return val
    else:
        return default_value

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
columns= sys.argv[3].split(",") # col1, col2, col3
separator= sys.argv[4] # - / ; _ 
column_name = sys.argv[5]


DF_data = pd.read_csv(data_path)

# join columns
DF_data[column_name] = DF_data[columns].apply(lambda x: separator.join(x.dropna().astype(str).values), axis=1)


print(DF_data[column_name])
DF_data.to_csv(output_path,index=False)