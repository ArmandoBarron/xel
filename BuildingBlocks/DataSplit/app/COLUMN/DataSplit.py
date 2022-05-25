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
column= sys.argv[3] #column to split
method_ds= sys.argv[4] #datetime, manual
date_format= validate_string(sys.argv[5],default_value="%Y-%m-%d") #for the datetime method
split_value =sys.argv[6] #fot the manual method


DF_data = pd.read_csv(data_path)


if method_ds == "DT":
    DF_data[column] = pd.to_datetime(DF_data[column], format=date_format)
    DF_data['day'] = DF_data[column].dt.day
    DF_data['month'] = DF_data[column].dt.month
    DF_data['year'] = DF_data[column].dt.year
if method_ds == "M":
    DF_data= DF_data.join(DF_data[column].str.split(split_value, expand=True))

print(DF_data)
DF_data.to_csv(output_path,index=False)