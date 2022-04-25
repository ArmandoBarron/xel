import os
import hashlib
from datetime import datetime
import zipfile
import tempfile
import pandas as pd
from random import randint
import time 
import logging

LOG = logging.getLogger()

### tools for compressed files ###
def zip_extraction(zipfile_path):
    
    dirpath = tempfile.mkdtemp()

    with zipfile.ZipFile(zipfile_path, 'r') as zipObj:
        # Extract all the contents of zip file in different directory
        list_of_files = zipObj.namelist()
        zipObj.extractall(dirpath)
    return dirpath,list_of_files

##################################

def CreateSolutionID(params_recived):
    if 'token_solution' in params_recived:
        RN=params_recived['token_solution']
    else:
        now = datetime.now()
        dt_string = now.strftime("%d/%m/%Y %H:%M:%S")
        id_string=  "%s-%s" %(dt_string, randint(10000,90000)) #random number with 10 digits
        encoded=id_string.encode()
        RN = hashlib.sha256(encoded).hexdigest()
    return RN

def createFolderIfNotExist(folder_name,wd=""):
    try:
        if not os.path.exists(wd+folder_name):
            os.makedirs(wd+folder_name)
    except FileExistsError:
        pass
    return wd+folder_name


def Request2Dataset(df_path,peticiones):
    df = pd.read_csv(df_path)
    results = []
    for p in peticiones: # it can be multilayer but for now its fine
        req = p['request']
        val = p['value']
        if req=="unique":
            res = df[val].unique().tolist()
            results.append(res)
        if req=="query":
            res = df.query(val)
            res = res.to_json(orient="records")
            results.append(res)

    return results

def DatasetDescription(datos):
    """
    create a json description form a pandas dataframe
    return: json with the keys ['columns','info'] 
    """
    columns = ['count','unique','top','freq','mean','std' ,'min' ,'q_25' ,'q_50' ,'q_75' ,'max']
    datos = datos.apply(pd.to_numeric, errors='ignore')
    response = dict()
    response['info']=dict()
    response['unique']=dict()
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
        typename =datos[col].dtype.name
        column_description['type'] = typename
        if typename=="object":
            LOG.error("Se encontraron unicos")
            response['unique'][col]=list(datos[col].unique()) # sagregan los valores unicos
        response['info'][col] = column_description
    

    return response

def FileExist(filepath):
    exist = os.path.exists(filepath)
    return exist

def GetExtension(filepath):
    try:
        fext= filepath.split(".")[-1]
    except Exception as e:
        fext = "folder"
    return fext

def GetFileDetails(filepath,filename):
    file_stats= {
        "filename":filename,
        "size":"%.2f MB" %(os.path.getsize(filepath)/(1024*1024)),
        "created at": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getctime(filepath))),
        "last modification": time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getmtime(filepath))),
        "last access":time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(os.path.getatime(filepath)))
    }
    return file_stats