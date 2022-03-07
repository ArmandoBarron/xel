import pandas as pd 
import json
import sys


def DatasetDescription(path_dataset,columns):
    datos = pd.read_csv(path_dataset)
    datos = datos[columns]
    columns = ['count','unique','top','freq','mean','std' ,'min' ,'q_25' ,'q_50' ,'q_75' ,'max']
    datos = datos.apply(pd.to_numeric, errors='ignore')
    response = dict()
    response['info']=dict()
    response['columns'] = list(datos.columns.values)
    des = datos.describe(include='all')
    for col in response['columns']:
        des_col = des[col]
        column_description = dict()
        for c in range(0,len(columns)):
            try:
                value = des_col[c]
            except Exception:
                break
            if pd.isnull(value) or pd.isna(value):
                value = ""
            column_description[columns[c]] = str(value)
        column_description['type'] = datos[col].dtype.name
        response['info'][col] = column_description
    return response





source_path =sys.argv[1]
destination =sys.argv[2]
process =sys.argv[3].upper()
columns =sys.argv[4].split(",") 

df = pd.read_csv(source_path) #READ CSV
print(columns)
df = df[columns] #filtter selected columns

if process == "CORRELATION":
    method_corr =sys.argv[5]
    result = json.loads(df.corr(method =method_corr).to_json(orient="columns"))
elif process=="COVARIANCE":
   result=  json.loads(df.cov().to_json(orient="columns"))
elif process=="DESCRIPTION":
    result = DatasetDescription(source_path,columns)
else: #statistical description
    result = DatasetDescription(source_path,columns)


with open('%sresult.json' %destination, 'w') as f:
    json.dump(result, f)