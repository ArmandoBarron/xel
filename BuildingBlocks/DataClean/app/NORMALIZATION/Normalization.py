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


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns
method = sys.argv[4] #min max, z-score


DF_data = pd.read_csv(data_path)
#print(DF_data[columns])


if method =="ZS":
    DF_data[columns] = DF_data[columns].apply(stats.zscore,nan_policy='omit')

if method =="MinMax":
    for col in columns:
        DF_data[col] = (DF_data[col] - DF_data[col].min()) / (DF_data[col].max() - DF_data[col].min())    

print(DF_data[columns])

DF_data.to_csv(output_path,index=False)