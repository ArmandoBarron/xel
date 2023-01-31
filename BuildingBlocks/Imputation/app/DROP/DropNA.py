import sys
import pandas as pd

def validate_int(val,default_value=0):
    if val != "" and val!="-":
        return int(val)
    else:
        return default_value


data_path= sys.argv[1] #data path
output_path= sys.argv[2] #output_path
columns= sys.argv[3].split(",") #columns
method= sys.argv[4] #all , any
n_na= validate_int(sys.argv[5]) #treshold
to_drop = validate_int(sys.argv[6]) #0=rows, 1=columns


DF_data = pd.read_csv(data_path)

if n_na>0:
    DF_data = DF_data.dropna(how=method,thresh=int(n_na), subset=columns,axis=to_drop)
else:
    DF_data = DF_data.dropna(how=method, subset=columns, axis=to_drop)


DF_data.to_csv(output_path,index=False)

