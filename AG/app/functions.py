import os
import hashlib
from datetime import datetime
import zipfile
import tempfile
import pandas as pd
from random import randint
import time 
import logging
import json
from chardet.universaldetector import UniversalDetector
import numpy as np
import csv



LOG = logging.getLogger()

### tools for compressed files ###
def zip_extraction(zipfile_path):
    
    dirpath = tempfile.mkdtemp()

    with zipfile.ZipFile(zipfile_path, 'r') as zipObj:
        # Extract all the contents of zip file in different directory
        list_of_files = zipObj.namelist()
        zipObj.extractall(dirpath)
    return dirpath,list_of_files


### tools for compressed files ###
def zip_creation(list_files_paths,filename,destination ):
    final_path =destination+filename+'.zip'
    with zipfile.ZipFile(final_path, 'w') as zipMe:        
        for file in list_files_paths:
            zipMe.write(file,os.path.basename(file))

    return final_path

def CompressFile(path_compressfile,path_results,ignore_list=[],namefile ="output.zip"):
    """
    path_compressfile::str -> /var/temp/
    path_results::str -> /var/temp/
    """
    fname = path_compressfile+namefile
    with zipfile.ZipFile(fname, 'w', zipfile.ZIP_DEFLATED) as zipObj:
    # Iterate over all the files in directory
        for folderName, subfolders, filenames in os.walk(path_results):
            for filename in filenames:
                print(filename)
                #create complete filepath of file in directory
                if filename not in ignore_list:
                    filePath = os.path.join(folderName, filename)
                    archive_file_path = os.path.relpath(filePath, path_results)
                    # Add file to zip
                    zipObj.write(filePath, archive_file_path)
                    #zipObj.write(filePath, os.path.relpath(filePath, src_path))

    return fname

##################################

def CreateFilesTree(list_files):
    tree = []
    for f in list_files:
        fpath = f.split("/")
        tree = recoursiveFolderTree(fpath,tree,f)
    return tree

def recoursiveFolderTree(fpath,tree,originalpath):
    list_p=fpath.copy()
    folder = fpath[0]
    del list_p[0]
    tmp = {"text":folder,"children":[]}

    
    existing_folder = next((item for item in tree if item["text"] == folder), None)
    if existing_folder is None:
        if len(fpath)>1:# its a folder
            tmp['children'] = recoursiveFolderTree(list_p, tmp['children'],originalpath)
        else: #its a file
            tmp = {"text":folder,"type":"file","path":originalpath, "id":originalpath}
        
        if tmp['text']!= "":
            tree.append(tmp)
        
    else:
        id_father = next((i for i, item in enumerate(tree) if item["text"] == folder))
        tree[id_father]['children'] = recoursiveFolderTree(list_p, tree[id_father]['children'],originalpath)
    
    return tree


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

def CreateDataToken(Token_solution,Task):
    id_string=  "%s/%s" %(Token_solution, Task) #random number with 10 digits
    encoded=id_string.encode()
    Token_data = hashlib.sha256(encoded).hexdigest()
    return Token_data

def validatePathIfSubtask(folder_name):
    if "-LVL-" in folder_name:
        if '-MAP-' in folder_name:
            folder_name = "datasets/" + folder_name

        if '-subtask-' in folder_name:
            folder_name = "products/" + folder_name

        folder_name = folder_name.replace("-VAL-","/")
        folder_name = folder_name.replace("-LVL-","/")
        folder_name = folder_name.replace("-MAP-","/")
        folder_name = folder_name.replace("-subtask-","/")
    
    return folder_name

def getMetadataFromPath(id_service):
    m = {}
    path_separator = "."
    #["product_type","product_kind","product_level","level_path","porfile","path"]
    list_metadata = []
    if "-LVL-" in id_service:
        level_id,other = id_service.split("-LVL-")

        if '-MAP-' in id_service:
            m["product_type"] = "dataview"
            other, m["product_kind"] =other.split("-MAP-")
        if '-subtask-' in id_service:
            m["product_type"] = "product"
            other, m["product_kind"] =other.split("-subtask-")

        i=0
        lvlpath = []
        lvlvalue = []
        for pairs in other.split("-VAL-"):
            i+=1
            key,value = pairs.split("=")
            lvlvalue.append(value)
            lvlpath.append(key)
        m["level_path"] = path_separator.join(lvlpath) 
        m["porfile"] = path_separator.join(lvlvalue) 
        m["product_level"] = i
        list_metadata = [m["product_type"],m["product_kind"],m["product_level"],m["level_path"],m["porfile"]]
    else:
        m["product_kind"] = id_service
        m["product_type"] = "product"
        m["product_level"] = 0
        list_metadata = [m["product_type"],m["product_kind"],m["product_level"],"",""]

    return list_metadata

def append_log_products(new_data,filename=""):
    fieldnames = ["product_type","product_kind","product_level","level_path","porfile","path"]

    if not os.path.exists(filename):
        # Si el archivo no existe, crea uno nuevo y escribe los encabezados
        with open(filename, mode="w", newline="") as file:
            writer = csv.DictWriter(file, fieldnames=fieldnames)
            writer.writeheader()

    # Abrir el archivo CSV en modo append
    with open(filename, mode="a", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(new_data)


def createFolderIfNotExist(folder_name,wd=""):
    try:
        folder_name =validatePathIfSubtask(folder_name)
        if not os.path.exists(wd+folder_name):
            os.makedirs(wd+folder_name,0o777)
    except FileExistsError:
        pass
    return wd+folder_name


def Request2Dataset(df_path,peticiones,return_type="json"):
    df = pd.read_csv(df_path)
    results = []
    LOG.error(peticiones)
    for p in peticiones: # it can be multilayer but for now its fine
        req = p['request']
        val = p['value']

        if req=="unique":
            res = df[val].unique().tolist()
            results.append(res)
        if req=="query":
            res = df.query(val)
            if len(res) <=0:
                val = val.replace("\"","")
                res = df.query(val)

            if return_type == "json":
                res = res.to_json(orient="records")
            
            results.append(res)
    #del df
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
    response['sample']=dict()
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
        #se añade el tipo de datos
        typename =datos[col].dtype.name
        column_description['type'] = typename
        #se añade la mediana
        if typename != "object":
            column_description['median'] = datos[col].median()
        # se cuentan nulos
        column_description['NaN'] = str(datos[col].isna().sum())
        #dataset de ejemplo
        response['sample'] = json.loads(datos.head(100).to_json(orient="records"))

        #if typename=="object":
        #    LOG.error("Se encontraron unicos en %s" % col)
        #    response['unique'][col] =list(datos[col].fillna("NaN").unique()) # sagregan los valores unicos
        
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

def TranslateBoolStr(var_str):
    if var_str =="True" or var_str =="TRUE" or var_str =="true":
        var_str = True
    else:
        var_str = False
    return var_str

def FormatParam(param):
    if isinstance(param, list):
        return ",".join([str(i) for i in param])
    elif isinstance(param, dict):
        return json.dumps(param)
    else:
        return str(param)
    
def FormatCommand(command,params,reserved_params={},default_none=True):
    """
    @{param}
    @{param::str::defult value}
    @{$ENV()}
    @{$REF::}

    """
    while True:
        #LOGER.error("command: %s" % command)
        start = command.find('@{') + 2
        if start==1: #given that -1 + 2 = 1
            break
        end = command.find('}', start)
        if start>end:
            return None
        parameter_found = command[start:end]
        #LOGER.error("---------------> %s" % parameter_found)
        ########## REPLACE PARAMS FOUND #############
        if parameter_found in reserved_params:
            command = command.replace("@{%s}" % parameter_found,reserved_params[parameter_found])
        elif parameter_found in params:
            temp_p = FormatParam(params[parameter_found]) #fillter the params to change it to a valid format (e.g a list [] to a string separated by commas)
            command = command.replace("@{%s}" % parameter_found,temp_p)
        else:
            #if the parameter does not exist, then a default - is allocated
            if default_none:
                command = command.replace("@{%s}" % parameter_found,"-")
            else:
                command = command.replace("@{%s}" % parameter_found,"")

    return command

def detect_encode(file):
    detector = UniversalDetector()
    detector.reset()
    with open(file, 'rb') as f:
        for row in f:
            detector.feed(row)
            if detector.done: break

    detector.close()
    return detector.result


