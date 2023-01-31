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

def validate_float(val,defult_value=0):
    if val != "" and val!="-":
        return float(val)
    else:
        return defult_value

data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns
outliers_detection= sys.argv[4] #(ZS) z-score, (IQR) Inter quartile, (M) manual
method = sys.argv[5] #eliminacion (del), nulificacion (NaN) 
n_standart_desviations = validate_int(sys.argv[6],3) 
min_range= validate_float(sys.argv[7])
max_range= validate_float(sys.argv[8])




DF_data = pd.read_csv(data_path)
#print(DF_data[columns])

data_4_detection = DF_data[columns]

if outliers_detection =="ZS":
    mask = (np.abs(stats.zscore(data_4_detection)) < n_standart_desviations)

if outliers_detection =="IQR":
    Q1 = data_4_detection.quantile (q = .25)
    Q3 = data_4_detection.quantile (q = .75)
    IQR = Q3 - Q1
    mask = ~((data_4_detection < (Q1 - 1.5 * IQR)) |(data_4_detection > (Q3 + 1.5 * IQR)))

if outliers_detection =="M":
    mask =  ( (data_4_detection >= min_range) & (data_4_detection <= max_range) )

print(mask)

if method == "DEL":
    DF_data = DF_data[mask.any(axis=1)]
if method == "NAN":
    DF_data[columns]=  np.where(~mask, np.nan, DF_data[columns])
    #DF_data=  pd.DataFrame(np.where(mask, np.nan, v), DF_data.index, DF_data.columns)


DF_data.to_csv(output_path,index=False)